# https://github.com/sherlock-project/sherlock
import tempfile
import random
from io import BytesIO
from executor.clean import clean_username, is_url, clean_file_line
from executor.run_proc import run_proc
from executor.func_res import FuncRes
from executor.executable import IExecutable


class Sherlock(IExecutable):
    @staticmethod
    def request(username: str, proxy: str | list[str] | None = None) -> FuncRes[BytesIO]:
        cleaned_username = clean_username(username)

        with tempfile.NamedTemporaryFile() as tmpfile:
            cmd = [
                "python3",
                "-m",
                "sherlock_project", 
                cleaned_username, 
                "--output", 
                tmpfile.name
            ]
            if proxy:
                if isinstance(proxy, list):
                    proxy = random.choice(proxy)
                cmd += ['--proxy', proxy]
            _res = run_proc(cmd, timeout=600)
            if _res.err:
                return _res
            
            tmpfile.seek(0)
            buf = BytesIO(tmpfile.read())
            buf.name = 'sherlock.txt'
            return FuncRes(val=buf)

    @staticmethod
    def parse(res: FuncRes[BytesIO]) -> FuncRes[list[str]]:
        if not res.val:
            return res
        res.val.seek(0)
        urls: list[str] = []
        for line in res.val.readlines():
            clean_line = clean_file_line(line)
            if is_url(clean_line):
                urls.append(clean_line)
        return FuncRes(val=urls)

    @staticmethod
    def interpretate(res: FuncRes[list[str]]) -> str:
        if not res.val:
            return ""
        text = "\n".join(f"🪪 {val}" for val in res.val)
        return text
