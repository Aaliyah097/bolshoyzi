from sqlalchemy import select
from db.clients.pg.tables.programs import Programs
from db.clients.pg.client import async_db_session
from .program import Program


async def get_programs(is_active: bool | None = None, names: list[str] | None = None) -> list[Program]:
    query = select(Programs)
    if is_active is not None:
        query = query.where(Programs.is_active == is_active)
    if names:
        query = query.where(Programs.name.in_(names))

    async with async_db_session() as session:
        result = (await session.execute(query)).scalars().all()
    
    return [Program(**row.to_dict()) for row in result]


async def get_program(name: str) -> Program | None:
    if not name:
        return None
    query = select(Programs).where(Programs.name == str(name))
    async with async_db_session() as session:
        result = (await session.execute(query)).scalar_one_or_none()
    return Program(**result.to_dict()) if result else None
