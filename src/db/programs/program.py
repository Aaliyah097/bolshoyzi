from db.entity import Entity
from dataclasses import dataclass


@dataclass
class Program(Entity):
    name: str
    label: str | None
    is_active: bool
    description: str | None
