from sqlalchemy import select
from db.clients.pg.client import async_db_session
from db.clients.pg.tables.scripts import Scripts
from db.scripts.script import Script, Program


async def get_scripts(
    is_active: bool | None = None,
    group: str | None = None,
    script_name: str | None = None
) -> list[Script]:
    query = select(Scripts)
    if is_active is not None:
        query = query.where(Scripts.is_active == is_active)
    if group is not None:
        query = query.where(Scripts.group == str(group))
    if script_name is not None:
        query = query.where(Scripts.name == str(script_name))

    async with async_db_session() as session:
        result = (await session.execute(query)).scalars().all()
    
        return [
            Script(
                id=row.id,
                created_at=row.created_at,
                updated_at=row.updated_at,
                name=row.name,
                label=row.label,
                description=row.description,
                is_active=row.is_active,
                group=row.group,
                input=row.input,
                programs=[
                    Program(
                        id=program.id,
                        created_at=program.created_at,
                        updated_at=program.updated_at,
                        name=program.name,
                        label=program.label,
                        is_active=program.is_active,
                        description=program.description
                    )
                    for program in row.programs
                ]
            )
            for row in result
        ]
