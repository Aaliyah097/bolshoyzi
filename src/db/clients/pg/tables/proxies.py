from sqlalchemy import Column, Text, DateTime, Boolean, Integer
from .base import Base


class Proxies(Base):
    __tablename__ = 'proxies'

    url = Column(Text, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    is_working = Column(Boolean, default=True)
    provider = Column(Text, nullable=True)
    expired_at = Column(DateTime, nullable=True)
    country = Column(Text, nullable=True)
    error = Column(Text, nullable=True)

    fails_count = Column(Integer, nullable=True)
    success_count = Column(Integer, nullable=True)
    fails_in_row = Column(Integer, nullable=True)
