from enum import StrEnum
from dataclasses import dataclass
from executor.func_res import FuncRes
from distributor.user_req import UserReq


class StorageEnum(StrEnum):
    MONGO = 'mongo'
    S3 = 's3'


@dataclass
class NamedError:
    program: str
    error: str

    def model_dump(self) -> dict:
        return {
            'program': self.program,
            'error': self.error 
        }

    def __hash__(self):
        return hash(self.error)


@dataclass
class TaskRes:
    user_req: UserReq  # кому отправлять и по какому ид искать
    errors: set[NamedError]  # что можно улучшить
    storages: set[StorageEnum]  # где искать

    def model_dump(self) -> dict:
        return {
            'user_req': self.user_req.model_dump(),
            'errors': [error.model_dump() for error in self.errors],
            'storages': list(self.storages)
        }
    
    @staticmethod
    def model_restore(data: dict) -> 'TaskRes':
        return TaskRes(
            user_req=UserReq(**data['user_req']),
            errors=[NamedError(**err) for err in data['errors']],
            storages=data['storages']
        )

    # TODO errors можно использовать следующим образом
    # если репорте сходит в базу и увидит, что там нет данных 
    # то отправит пользователю список ошибок
    # а если данные есть, но и ошибки тоже есть
    # то к ответу добавит фразу типа "Можно улучшить качество поиска, если исправить следующие ошибки"

    # TODO может быть проблема, что текста ошибок будут иметь технический характери
    # например, что прокси упал
