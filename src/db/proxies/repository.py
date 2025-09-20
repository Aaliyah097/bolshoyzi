from datetime import datetime
from sqlalchemy import select, update
from db.clients.pg.tables.proxies import Proxies
from db.clients.pg.tables.ip_sites import IpSites
from db.clients.pg.client import async_db_session
from .proxy import Proxy
from .ip_site import IpSite
import logging


async def request_proxies(is_working: bool | None = None) -> list[Proxy]:
    async with async_db_session() as session:
        query = select(Proxies)
        if is_working is not None:
            query = query.where(Proxies.is_working == is_working)
        result = (await session.execute(query)).scalars().all()
    return [Proxy(**row.to_dict()) for row in result]


async def get_ip_sites(is_working: bool | None = None) -> list[IpSite]:
    async with async_db_session() as session:
        query = select(IpSites)
        if is_working:
            query = query.where(IpSites.is_working == is_working)
        result = (await session.execute(query)).scalars().all()
    return [IpSite(**row.to_dict()) for row in result]


async def mark_ip_site(ip_site_id: str, is_working: bool, error: str | None):
    async with async_db_session() as session:
        ip_site = await session.get(IpSites, str(ip_site_id))
        if not ip_site:
            logging.error(f"Айпи сайт с ИД {ip_site_id} не найден")
            return

        ip_site.is_working=bool(is_working)
        ip_site.error=error
        ip_site.verified_at=datetime.now()
        if is_working:
            ip_site.fails_in_row=0 
        else:
            ip_site.fails_in_row += 1
        ip_site.success_count += int(is_working)
        ip_site.fails_count += int(not is_working)


async def mark_proxy(proxy_id: int, is_working: bool, error: str | None):
    async with async_db_session() as session:
        proxy = await session.get(Proxies, str(proxy_id))
        if not proxy:
            logging.error(f"Прокси с ИД {proxy_id} не найден")
            return

        proxy.is_working=bool(is_working)
        proxy.error=error
        proxy.verified_at=datetime.now()
        if is_working:
            proxy.fails_in_row=0 
        else:
            proxy.fails_in_row += 1
        proxy.success_count += int(is_working)
        proxy.fails_count += int(not is_working)
