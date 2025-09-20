import os
import json
import aio_pika
import asyncio
from distributor.user_req import UserReq
from db.clients.rabbit.client import RabbitMQClient
import logging
from db.settings.creds import creds
from db.scripts.repository import get_scripts
from executor.finder import FIND, IAsyncExecutable
from distributor.script_res import ScriptRes, NamedFuncRes
from distributor.storage import store_parsed_script_res, store_raw_script_res
from db.proxies.repository import request_proxies
from db.clients.mongo.client import close_client as close_mongo_client, create_tasks_results_idx
from reporter.task_res import TaskRes, StorageEnum, NamedError
from db.scripts.script import Script
from concurrent.futures import ProcessPoolExecutor
from db.results.repository import get_result, save_result


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
CPUS_COUNT = os.cpu_count() - 1
tasks_rabbit = RabbitMQClient(creds.rabbitmq_conn_string, 'tasks')
results_rabbit = RabbitMQClient(creds.rabbitmq_conn_string, 'results')
pool_executor = ProcessPoolExecutor(max_workers=CPUS_COUNT)


async def _consume_tasks():
    async with tasks_rabbit.queue.iterator() as queue_iter:
        async for message in queue_iter:
            try:
                body = json.loads(message.body.decode())
                user_req = UserReq(**body)
            except Exception as exc:
                logging.error("Задача отклонена", exc, exc_info=True)
                await message.reject(requeue=False)
                continue
            asyncio.create_task(_handle_user_request(user_req, message))
            logging.info(f"Принята новая задача {user_req}")


async def _handle_user_request(user_req: UserReq, message: aio_pika.IncomingMessage):
    try:
        ex_res = await get_result(user_req.req_id)
        # проверяем может результат для такого запроса уже был высчитан ранее
        if not ex_res:
            scripts = await get_scripts(is_active=True, script_name=user_req.script_name)
            if not scripts:
                logging.error(f"Скрипт с названием '{user_req.script_name}' не найден, задача отклонена", exc_info=True)
                await message.reject(requeue=False)
                return
       
            proxy = [proxy.url for proxy in await request_proxies(is_working=True)]

            raw_task_res, parsed_task_res = await _distribute_request(user_req, scripts, proxy)

            _tasks = []
            errors, raw_task_res = _extract_errors_from_results(raw_task_res)
            if raw_task_res.results:
                _tasks.append(store_raw_script_res(raw_task_res))
            if errors:
                logging.warning(f"Одна из программ завершилась с ошибкой {errors}")

            parsed_errors, parsed_task_res = _extract_errors_from_results(parsed_task_res)
            if parsed_task_res.results:
                _tasks.append(store_parsed_script_res(parsed_task_res))
                # сохраняем в кэш, если нашлось что-то полезное
                _tasks.append(save_result(user_req.req_id, scripts[0].name, user_req.payload))
            if parsed_errors:
                logging.warning(f"Не удалось распарсить результат одной из задач {parsed_errors}")

            if _tasks:
                await asyncio.gather(*_tasks)
        else:
            logging.info("Найден и отправлен существующий результат")
            errors = []
        await results_rabbit.send(
            TaskRes(
                user_req=user_req,
                errors=errors,
                storages=[StorageEnum.MONGO, StorageEnum.S3]
            ).model_dump()
        )
    except Exception as exc:
        logging.error("Задача возвращена в очередь", exc, exc_info=True)
        # повторяем задачу потому что явно сетевой сбой, а не угроза
        await message.reject(requeue=True)
        return
    await message.ack()


def _extract_errors_from_results(script_res: ScriptRes) -> tuple[set[NamedError], ScriptRes]:
    errors: set[str] = set()
    _results: list[NamedFuncRes] = []
    for result in script_res.results:
        val, err = result.func_res
        if err:
            errors.add(NamedError(program=result.program, error=str(err)))
        if not err and val:
            _results.append(result)
    script_res.results = _results
    return errors, script_res 


async def _distribute_request(user_req: UserReq, scripts: list[Script], proxy: list[str]) -> tuple[ScriptRes, ScriptRes]:
    """return: tuple[raw_task_res, parsed_task_res]"""
    raw_task_res = ScriptRes(user_req=user_req, results=[])
    parsed_task_res = ScriptRes(user_req=user_req, results=[])
    
    for program in scripts[0].programs:
        if not program.is_active:
            continue
        pcls = FIND.get(program.name)
        if not pcls:
            logging.info(f"Программа {program} не найдена в файндере")
            continue
        if isinstance(pcls(), IAsyncExecutable):
            logging.info(f"Запущена программа {pcls} в асинхроном режиме")
            raw_exec_res = await pcls.request(user_req.payload, proxy=proxy)
        else:
            logging.info(f"Запущена программа {pcls} в мультипроцессорном режиме")
            loop = asyncio.get_running_loop()
            raw_exec_res = await loop.run_in_executor(
                pool_executor,
                pcls.request,
                user_req.payload,
                proxy
            )
        if pcls.__need_parsing__:
            raw_task_res.results.append(
                NamedFuncRes(
                    program=program.name,
                    func_res=raw_exec_res
                )
            )
            parsed_exec_res = pcls.parse(raw_exec_res)
        else:
            parsed_exec_res = raw_exec_res
        logging.info("Результат работы передан в службу уведомлений")
        parsed_task_res.results.append(
            NamedFuncRes(
                program=program.name,
                func_res=parsed_exec_res
            )
        )
    
    return raw_task_res, parsed_task_res


async def main():
    await results_rabbit.connect()
    logging.info("Очередь задач подключена")
    await tasks_rabbit.connect()
    logging.info("Очередь результатов подключена")
    await create_tasks_results_idx()
    logging.info("Индекс для монги создан")
    try:
        await _consume_tasks()
    except Exception as exc:
        logging.error(exc, exc_info=True)
    finally:
        await results_rabbit.close()
        await tasks_rabbit.close()
        logging.info("Рэбит закрыт")
        close_mongo_client()
        logging.info("Монга закрыта")
        pool_executor.shutdown(wait=True)
        logging.info("Пул закрыт")


if __name__ == '__main__':
    asyncio.run(main())
