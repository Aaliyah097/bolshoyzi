from typing import TypeVar
from abc import ABC, abstractmethod
from executor.func_res import FuncRes


RAW = TypeVar('T')
PARSED = TypeVar('T')


class IParse(ABC):
    __need_parsing__: bool = True

    @staticmethod
    @abstractmethod
    def parse(res: FuncRes[RAW]) -> FuncRes[PARSED]:
        pass

    @staticmethod
    @abstractmethod
    def interpretate(res: FuncRes[PARSED]) -> str:
        pass


class IExecutable(IParse):
    @staticmethod
    @abstractmethod
    def request(*args, proxy: str | list[str] | None = None, **kwargs) -> FuncRes[RAW]:
        pass


class IAsyncExecutable(IParse):
    @staticmethod
    @abstractmethod
    async def request(*args, proxy: str | list[str] | None = None, **kwargs) -> FuncRes[RAW]:
        pass
