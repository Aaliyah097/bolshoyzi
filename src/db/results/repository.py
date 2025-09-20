from db.results.result import Result
from sqlalchemy import select
from db.clients.pg.client import async_db_session, AsyncSession
from db.clients.pg.tables.results import Results


async def _get_by_req_id(session: AsyncSession, req_id: str) -> Result | None:
    query = select(Results).where(Results.req_id == str(req_id))
    result = (await session.execute(query)).scalar_one_or_none()
    return Result(**(result.to_dict())) if result else None


async def get_result(req_id: str) -> Result | None:
    async with async_db_session() as session:
        return await _get_by_req_id(session, req_id)


async def save_result(req_id: str, script_name: str, payload: str):
    async with async_db_session() as session:
        if await _get_by_req_id(session, req_id):
            return
        new_res = Results(
            req_id=str(req_id),
            script_name=str(script_name),
            payload=str(payload)
        )
        session.add(new_res)
