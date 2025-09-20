from sqlalchemy import Column, Boolean, Integer
from .base import Base


class Settings(Base):
    __tablename__ = 'settings'

    is_debug = Column(Boolean, nullable=False)
    proxies_monitor_interval_sec = Column(Integer, nullable=False)
    autoheal_interval_hours = Column(Integer, nullable=False)
