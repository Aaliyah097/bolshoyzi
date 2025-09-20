from dataclasses import dataclass
from datetime import datetime


@dataclass
class Entity:
    id: str
    created_at: datetime
    updated_at: datetime
