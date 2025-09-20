from sqlalchemy import Column, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from .scripts_programs import scripts_programs
from .programs import Programs


class Scripts(Base):
    __tablename__ = "scripts"

    name = Column(Text, nullable=False, unique=True)
    label = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    group = Column(Text, nullable=True)
    input = Column(Text, nullable=True)

    programs = relationship(
        "Programs",
        secondary=scripts_programs,
        back_populates="scripts",
        lazy="selectin"
    )
