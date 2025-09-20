from sqlalchemy import Column, Text, DateTime, Boolean, Integer
from .base import Base


class IpSites(Base):
    __tablename__ = 'ip_sites'

    url = Column(Text, nullable=False)
    is_working = Column(Boolean, nullable=False, default=True)
    verified_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)

    fails_count = Column(Integer, nullable=True)
    success_count = Column(Integer, nullable=True)
    fails_in_row = Column(Integer, nullable=True)
