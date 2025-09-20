from dataclasses import dataclass
import logging
from db.clients.pg.client import async_db_session
from sqlalchemy import select
from db.clients.pg.tables.settings import Settings as SettingsTable


@dataclass
class Params:
    DEBUG: bool
    AUTOHEAL_INTERVAL_HOURS: int
    PROXIES_MONITOR_INTERVAL_SEC: int


async def get_params() -> Params:
    query = select(SettingsTable).order_by(SettingsTable.created_at.desc()).limit(1)
    async with async_db_session() as session:
        result = (await session.execute(query)).scalar_one_or_none()
    if not result:
        raise ValueError("Не найдены настройки в БД !")
    logging.info("Подгружены настройки из БД")
    return Params(
        DEBUG=bool(result.is_debug),
        AUTOHEAL_INTERVAL_HOURS=int(result.autoheal_interval_hours),
        PROXIES_MONITOR_INTERVAL_SEC=int(result.proxies_monitor_interval_sec)
    )
