from sqlalchemy import Column, Boolean, Integer, String, ForeignKey
from .base import Base


class Results(Base):
    __tablename__ = 'results'

    script_name = Column(ForeignKey("scripts.name"), index=True)
    payload = Column(String, nullable=False, index=True)
    req_id = Column(String, nullable=False, index=True, unique=True)
