import typing as T
import subprocess
from executor.func_res import FuncRes
import logging


def run_proc(
    command: list[T.Any],
    timeout: int = 60
) -> FuncRes[subprocess.CompletedProcess]:
    if not command or not isinstance(command, list):
        return FuncRes(err = ValueError("Невалидный ввод"))
    try:
        result: subprocess.CompletedProcess = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        logging.error(command, exc)
        return FuncRes(err = TimeoutError("Истекло время на выполнение задачи"))

    if result.returncode != 0:
        logging.error(command, result.stderr, result.stdout)
        return FuncRes(err = RuntimeError(result.stderr))

    return FuncRes(val=result)
