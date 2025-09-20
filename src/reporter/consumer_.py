import json
import random
import aiohttp
import asyncio
import logging
from distributor.script_res import NamedFuncRes
from distributor.user_req import UserReq
from reporter.task_res import TaskRes, NamedError, StorageEnum
from db.clients.rabbit.client import RabbitMQClient
from db.settings.creds import creds
from db.clients.mongo.client import close_client as close_mongo_client
from distributor.storage import get_parsed_task_res, get_raw_task_res
from executor.finder import FIND
from db.scripts.repository import get_scripts
from db.programs.repository import get_program


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
results_rabbit = RabbitMQClient(creds.rabbitmq_conn_string, 'results')
tgbot_http_session: aiohttp.ClientSession | None = None
BOOKS_ICONS = ['📔', '📕', '📗', '📘', '📙']


async def _consume_tasks():
    async with results_rabbit.queue.iterator() as queue_iter:
        async for message in queue_iter:
            try:
                body = json.loads(message.body.decode())
                task_res = TaskRes.model_restore(body)
                logging.info(f"Поступил новый результат задачи {task_res}")
            except Exception as exc:
                logging.error("Результат отклонен", exc)
                await message.reject(requeue=False)
                continue
            parsed_res = await get_parsed_task_res(task_res.user_req.req_id)
            report = await _make_parsed_report(parsed_res)
            await _notify_user(task_res.user_req, report)
            await message.ack()


async def _make_parsed_report(parsed_res: list[NamedFuncRes]) -> str:
    report = """"""
    for res in parsed_res:
        if res.program not in FIND:
            continue
        program = await get_program(res.program)
        if not program:
            continue
        text_result = FIND[res.program].interpretate(res.func_res)
        if report:
            report += "───────────────\n\n"
        rep = (
            f"{random.choice(BOOKS_ICONS)} *{program.label}*\n\n"
            f">{program.description}\n\n"
            "Вот, что удалось найти:\n"
            f"{text_result}\n"
        )
        report += rep
    if not report:
        return "Не удалось ничего найти 🥲"
    return report.replace('.', '\\.').replace("=", '\\=')


async def _notify_user(user_req: UserReq, report: str) -> bool:
    global tgbot_http_session
    if not tgbot_http_session:
        tgbot_http_session = aiohttp.ClientSession(
            base_url=f"https://api.telegram.org/bot{creds.TGBOT_API_KEY}/"
        )
    response = await tgbot_http_session.post(
        url='sendMessage', 
        json={
            "chat_id": user_req.user_id,
            "text": report,
            "parse_mode": "MarkdownV2",
            "reply_markup": {
                "inline_keyboard": [
                [
                    {
                    "text": "🏠 Главное меню",
                    "callback_data": "group:home"
                    }
                ]
                ]
            }
        }
    )
    data = await response.json()
    if not data['ok']:
        logging.error(data)
        return False
    return True

async def main():
    await results_rabbit.connect()
    try:
        await _consume_tasks()
    except Exception as exc:
        logging.error(exc)
    finally:
        await results_rabbit.close()
        close_mongo_client()
        if tgbot_http_session:
            await tgbot_http_session.close()


if __name__ == '__main__':
    asyncio.run(main())
