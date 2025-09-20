from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import sessionmaker

from db.settings.creds import creds


pg_engine: AsyncEngine = create_async_engine(
    creds.async_pg_conn_string, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800
)
session_maker = sessionmaker(
    pg_engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)


@asynccontextmanager
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise exc
