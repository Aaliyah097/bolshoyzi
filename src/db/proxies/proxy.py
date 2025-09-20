from db.entity import Entity
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Proxy(Entity):
    url: str
    verified_at: datetime | None
    is_working: bool | None
    provider: str | None
    expired_at: datetime | None
    country: str | None
    error: str | None
    fails_count: int
    success_count: int
    fails_in_row: int
