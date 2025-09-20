import asyncio
from io import BytesIO
from distributor.script_res import ScriptRes, NamedFuncRes, FuncRes
from db.clients.mongo.client import get_client as get_mongo_client
from db.clients.s3.s3_client import get_client as get_s3_client
from db.settings.creds import creds
import logging


async def store_parsed_script_res(script_res: ScriptRes):
    collection = get_mongo_client()[creds.MONGO_DB_NAME]['tasks_results']
    usefull_data = {
        'req_id': script_res.user_req.req_id,
        'results': [res.model_dump() for res in script_res.results]
    }
    await collection.replace_one(
        {"req_id": script_res.user_req.req_id},
        usefull_data,
        upsert=True
    )


async def store_raw_script_res(script_res: ScriptRes):
    async with get_s3_client() as client:
        tasks: list[asyncio.Task] = []
        for res in script_res.results:
            val, _ = res.func_res
            if not val:
                logging.warning("Отсутствует файл ждя сохранения в С3", script_res.user_req)
                continue
            if not isinstance(val, BytesIO):
                logging.warning("Была попытка сохранить в С3 не файл", script_res.user_req)
                continue
            if not hasattr(val, 'name'):
                logging.warning("Пришел файл без имени", script_res.user_req)
                continue
            file_key = f"{script_res.user_req.req_id}/{val.name}"
            val.seek(0)
            tasks.append(
                asyncio.create_task(
                    client.upload_fileobj(
                        val, 
                        creds.S3_BUCKET,
                        file_key
                    )
                )
            )
        await asyncio.gather(*tasks)


async def get_parsed_task_res(req_id: str) -> list[NamedFuncRes]:
    collection = get_mongo_client()[creds.MONGO_DB_NAME]['tasks_results']
    doc = await collection.find_one({"req_id": req_id})
    if not doc:
        return []
    return [
        NamedFuncRes(
            program=res['program'],
            func_res=FuncRes(
                val=res['func_res'][0],
                err=res['func_res'][1]
            )
        )
        for res in doc['results']
    ]


async def get_raw_task_res(req_id: str) -> list[NamedFuncRes]:
    pass
