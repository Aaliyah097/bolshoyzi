from dataclasses import dataclass
from datetime import datetime
from db.entity import Entity


@dataclass
class IpSite(Entity):
    url: str
    is_working: bool
    verified_at: datetime | None
    error: str | None
    fails_count: int
    success_count: int
    fails_in_row: int
