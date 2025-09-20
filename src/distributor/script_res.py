from dataclasses import dataclass
from executor.func_res import FuncRes
from distributor.user_req import UserReq


@dataclass
class NamedFuncRes:
    program: str
    func_res: FuncRes

    def model_dump(self) -> dict:
        return {
            'program': self.program,
            'func_res': self.func_res
        }


@dataclass
class ScriptRes:
    user_req: UserReq
    results: list[NamedFuncRes]

    def model_dump(self) -> dict:
        return {
            'user_req': self.user_req.model_dump(),
            'results': [res.model_dump() for res in self.results],
        }
