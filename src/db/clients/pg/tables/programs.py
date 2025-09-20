from sqlalchemy import Column, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from .scripts_programs import scripts_programs


# TODO можно добавить таблицу инпутов, то есть того, 
# что принимает на вход программа, тогда можно получить все программы
# по конкретному инпуту, таким образом понять какая информация может быть
# вывлена от конкретных данных, а еще добавить аутпут - информация-результат
# работы программы

class Programs(Base):
    __tablename__ = 'programs'

    name = Column(Text, nullable=False)
    label = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    description = Column(Text, nullable=True)

    scripts = relationship(
        "Scripts",
        secondary=scripts_programs,
        back_populates="programs"
    )