from typing import List

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Unit(Base):
    __tablename__ = 'units'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    # Relationship to variables
    variables: Mapped[List['Variable']] = relationship('Variable', back_populates='unit')
