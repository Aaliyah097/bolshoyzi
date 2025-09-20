import ulid
from sqlalchemy import select, and_, insert
from dataclasses import asdict
from datetime import datetime
from db.clients.pg.client import async_db_session
from db.scripts.script import Script
from db.programs.program import Program
from db.scripts.script_group import ScriptGroup
from db.scripts.script_input import ScriptInput
from db.clients.pg.tables.programs import Programs
from db.clients.pg.tables.scripts import Scripts
from db.clients.pg.tables.scripts_programs import scripts_programs


SCRIPTS_LIST: list[Script] = [
    Script(
        id=str(ulid.new()), 
        created_at=datetime.now(), 
        updated_at=datetime.now(),
        name="my_email",
        label="Учетки на Мою почту",
        description="Посмотреть на каких сайтах есть учетные записи, зарегистрированные на мой адрес электронной почты",
        is_active=True,
        group=ScriptGroup.ME,
        input=ScriptInput.EMAIL,
        programs=[
            Program(
                str(ulid.new()),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                name='sherlock',
                label='Шерлок',
                is_active=True,
                description="Выдает список ссылок на карточки пользователей с разных сайтов, которые зарегистрированы на мою почту"
            ),
        ]
    ),
    Script(
        id=str(ulid.new()),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        name='my_username',
        label='Учетки на мой юзернейм',
        description="Посмотреть на каких сайтах есть учетные записи, зарегистрированные на мой юзернейм",
        is_active=True,
        group=ScriptGroup.ME,
        input=ScriptInput.USERNAME,
        programs=[
            Program(
                str(ulid.new()),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                name='socialscan',
                label='Социалскан',
                is_active=True,
                description="Выдает список ссылок на карточки пользователей с разных сайтов, которые зарегистрированы на мой юзернейм"
            )
        ]
    )
]


async def preload():
    async with async_db_session() as session:
        for script in SCRIPTS_LIST:
            for program in script.programs:
                if ex_program := (
                    await session.execute(
                        select(Programs).where(Programs.name == program.name).limit(1)
                    )
                ).scalar_one_or_none():
                    program.id = ex_program.id 
                    continue
                session.add(Programs(**asdict(program)))
            await session.flush()
            
            _script_as_dict = asdict(script)
            del _script_as_dict['programs']
            if ex_script := (
                await session.execute(
                    select(Scripts).where(Scripts.name == script.name).limit(1)
                )
            ).scalar_one_or_none():
                script.id = ex_script.id
            else:
                session.add(Scripts(**_script_as_dict))
                await session.flush()
            
            for program in script.programs:
                if (
                    await session.execute(
                        select(scripts_programs).where(
                            and_(
                                scripts_programs.c.script_id == script.id,
                                scripts_programs.c.program_id == program.id
                            )
                        ).limit(1)
                    )
                ).scalar_one_or_none():
                    continue
                await session.execute(
                    insert(scripts_programs).values(
                        script_id=script.id,
                        program_id=program.id,
                        desc=f"{script.name} -> {program.name}"
                    )
                )
