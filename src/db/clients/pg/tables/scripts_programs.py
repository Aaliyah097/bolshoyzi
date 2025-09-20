from sqlalchemy import Column, Text, Table, ForeignKey
from .base import Base


scripts_programs = Table(
    "scripts_programs",
    Base.metadata,
    Column("script_id", ForeignKey("scripts.id"), primary_key=True),
    Column("program_id", ForeignKey("programs.id"), primary_key=True),
    Column('desc', Text, nullable=True)
)
