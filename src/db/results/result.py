from dataclasses import dataclass
from db.entity import Entity


@dataclass
class Result(Entity):
    script_name: str
    req_id: str
    payload: str
