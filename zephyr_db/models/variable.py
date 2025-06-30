from typing import List

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Variable(Base):
    """Measured weather variable type."""

    __tablename__ = 'variables'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    unit_id: Mapped[int] = mapped_column(ForeignKey('units.id'))

    unit: Mapped['Unit'] = relationship('Unit', back_populates='variables')

    station_variables: Mapped[List['StationVariable']] = relationship(
        'StationVariable', back_populates='variable'
    )

    observations = relationship('Observation', back_populates='variable')
