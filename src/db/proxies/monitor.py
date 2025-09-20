import re
import random
import asyncio
import aiohttp
from datetime import datetime 
from .repository import request_proxies, get_ip_sites, mark_ip_site, mark_proxy
from db.settings.params import get_params, Params
from .ip_site import IpSite
from .proxy import Proxy
import logging


PARAMS: Params | None = None
IPV4_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


async def _request_ip(session: aiohttp.ClientSession, url: str, proxy_url: str | None) -> str:
    response = await session.get(url, timeout=aiohttp.ClientTimeout(total=3), proxy=proxy_url)
    response_text = await response.text()
    if response.status != 200:
        raise ValueError("Код ответа не 200 ->", response.status, response_text)
    match = IPV4_REGEX.search(response_text)
    if not match:
        raise ValueError("Неожиданный текст ответа ->", response.status, response_text)
    return str(match)


def _can_be_autohealed(proxy_or_ip_site: Proxy | IpSite, now: datetime) -> bool:
    if proxy_or_ip_site.is_working:
        return True
    return (now - proxy_or_ip_site.verified_at).total_seconds() > PARAMS.AUTOHEAL_INTERVAL_HOURS * 60 * 60


async def get_my_ip_site(ip_sites: list[IpSite]) -> tuple[IpSite, str]:
    random.shuffle(ip_sites)
    now = datetime.now()

    for ip_site in ip_sites:
        # Если прошло достаточно времени после последней ошибки, то даем шанс восстановиться в работе
        if not _can_be_autohealed(ip_site, now):
            logging.warning(f"Айпи сайт {ip_site.url} временно отдыхает")
            continue
        async with aiohttp.ClientSession() as session:
            try:
                ip = await _request_ip(session, ip_site.url, proxy_url=None) 
                # Возвращаем ранее ошибочный сайт в пул доверенных
                await mark_ip_site(ip_site_id=ip_site.id, is_working=True, error=None)
                logging.info(f"Айпи сайт {ip_site.url} подошел для проверки айпи")
                return (ip_site, ip)
            except Exception as exc:
                # Помечаем сайт ошибочным и отправляем на временный отдых
                logging.warning(f"Айпи сайт {ip_site.url} отправляется в бан")
                await mark_ip_site(ip_site_id=ip_site.id, is_working=False, error=str(type(exc)) + " " + str(exc))
    else:
        # Если ни один сайт не дал позитивного ответа, значит пора вмешиваться вручную
        raise ValueError("На данный момент нет рабочих сайтов для проверки IP !")


def _check_proxy_ttl(proxy: Proxy, now: datetime):
    if not proxy.expired_at:
        logging.warning(f"Для прокси {proxy.url} не установлено время истечения срока действия !")
    days_left = (proxy.expired_at - now).total_seconds() / 60 / 60 / 24
    if int(days_left) in [7, 3, 1]:
        logging.warning(f"Для прокси {proxy.url} осталось {int(days_left)} дней")
    if int(days_left) <= 0:
        logging.error(f"Закончился срок действия прокси {proxy.url}")


async def verify_proxies():
    ip_sites = await get_ip_sites()
    test_ip_site, my_ip = await get_my_ip_site(ip_sites)
    
    proxies = await request_proxies()
    random.shuffle(proxies)
    now = datetime.now()

    semaphore = asyncio.Semaphore(10)
    async def _verifiy_proxy(proxy: Proxy, now: datetime) -> int:
        _check_proxy_ttl(proxy, now)
        if not _can_be_autohealed(proxy, now):
            logging.warning(f"Прокси {proxy.url} временно отдыхает")
            return 1

        async with semaphore:
            async with aiohttp.ClientSession() as session:
                try:
                    ip = await _request_ip(session, test_ip_site.url, proxy_url=proxy.url)
                    if str(ip) == str(my_ip) and not PARAMS.DEBUG:  # TODO
                        raise ValueError("Ошибка прокси, айпи адрес не изменился")
                    logging.info(f"Прокси {proxy.url} прошел проверку")
                    await mark_proxy(proxy_id=proxy.id, is_working=True, error=None)
                    return 0
                except Exception as exc:
                    logging.warning(f"Прокси {proxy.url} отправляется в бан")
                    await mark_proxy(proxy_id=proxy.id, is_working=False, error=str(type(exc)) + " " + str(exc))
                    return 1

    results = await asyncio.gather(*[_verifiy_proxy(proxy, now) for proxy in proxies])
    if sum(results) == len(proxies):
        raise ValueError("На данный момент нет рабочих прокси !")


async def main():
    global PARAMS
    PARAMS = await get_params()
    await verify_proxies()
    await asyncio.sleep(PARAMS.PROXIES_MONITOR_INTERVAL_SEC)


if __name__ == '__main__':
    asyncio.run(main())
