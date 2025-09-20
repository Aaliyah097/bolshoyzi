# https://github.com/iojw/socialscan
import tempfile
from io import BytesIO
import json
from executor.clean import clean_username_or_email
from executor.run_proc import run_proc
from executor.func_res import FuncRes
import logging
from executor.executable import IAsyncExecutable, IExecutable, IParse
from socialscan.util import Platforms, execute_queries


class ParseSocialScan(IParse):
    @staticmethod
    def parse(res: FuncRes[BytesIO]) -> FuncRes[list[str]]:
        if not res.val:
            return res
        data: dict = json.loads(res.val.read())
        platforms: list[str] = []
        try:
            for platform in list(data.values())[0]:
                try:
                    if (
                        not platform['success'] == 'True' or 
                        not platform['valid'] == 'True'
                    ):
                        continue
                    if platform['available'] == 'False':
                        platforms.append(platform.get('link') or platform.get('platform'))
                except KeyError as exc:
                    logging.error("Изменилась схема данных socialscan", exc, data)
                    return FuncRes(err=exc)
        except IndexError:
            pass

        return FuncRes(val=platforms)

    @staticmethod
    def interpretate(res: FuncRes[list[str]]) -> str:
        if not res.val:
            return ""
        text = "\n".join(f"🪪 {val}" for val in res.val)
        return text


class SocialScan(IExecutable, ParseSocialScan):
    @staticmethod
    def request(username_or_email: str, proxy: str | list[str] | None = None) -> FuncRes[BytesIO]:
        try:
            cleaned_username_or_email = clean_username_or_email(username_or_email)
        except ValueError as exc:
            return FuncRes(err=exc)
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w+') as proxy_file:
            with tempfile.NamedTemporaryFile(suffix=".json") as tmpfile:
                cmd = [
                    "socialscan",
                    cleaned_username_or_email,
                    "--json",
                    tmpfile.name,
                ]
                if proxy:
                    if not isinstance(proxy, list):
                        proxy = [proxy]
                    proxy_file.writelines((proxy_url + "\n" for proxy_url in proxy))
                    proxy_file.flush()
                    cmd += [
                        '--proxy-list',
                        proxy_file.name
                    ]
                _res = run_proc(cmd, timeout=600)
                if _res.err:
                    return _res

                buf = BytesIO(tmpfile.read())
                buf.name = 'socialscan.json'
                return FuncRes(val=buf)


class AsyncSocialscan(IAsyncExecutable, ParseSocialScan):
    # TODO сомнительной полезности программа, ищет только файерфокс бесполезный
    __need_parsing__: bool = False
    
    @staticmethod
    async def request(username_or_email: str, proxy: str | list[str] | None = None) -> FuncRes[list[str]]:
        try:
            cleaned_username_or_email = clean_username_or_email(username_or_email)
        except ValueError as exc:
            return FuncRes(err=exc)
        results = await execute_queries([cleaned_username_or_email], proxy_list=proxy)
        
        platforms: list[str] = []
        for platform in results:
            try:
                if (
                    not platform.success or 
                    not platform.valid
                ):
                    continue
                if not platform.available:
                    platforms.append(platform.link or str(platform.platform))
            except AttributeError as exc:
                logging.error("Изменилась схема данных асинхронного socialscan", exc, platforms)
                return FuncRes(err=exc)

        return FuncRes(val=platforms)

    @staticmethod
    def parse(res: FuncRes[list[str]]) -> FuncRes[list[str]]:
        return res
