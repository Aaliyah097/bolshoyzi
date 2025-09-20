from db.entity import Entity
from dataclasses import dataclass
from db.programs.program import Program


@dataclass
class Script(Entity):
    name: str
    label: str | None
    description: str | None
    is_active: bool
    group: str | None
    input: str | None
    programs: list[Program]
