from typing import NamedTuple, Generic, TypeVar, Optional


T = TypeVar("T")


class FuncRes(NamedTuple, Generic[T]):
    val: Optional[T] = None
    err: Optional[Exception] = None
