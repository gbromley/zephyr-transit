from typing import List

from sqlalchemy import REAL, BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Station(Base):
    """Weather station location and metadata."""

    __tablename__ = 'stations'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey('sources.id'))
    name: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(REAL, nullable=False)
    longitude: Mapped[float] = mapped_column(REAL, nullable=False)
    elevation: Mapped[float] = mapped_column(REAL, nullable=True)
    road_name: Mapped[str] = mapped_column(String, nullable=True)
    road_direction: Mapped[str] = mapped_column(String, nullable=True)

    observations: Mapped[List['Observation']] = relationship(
        'Observation', back_populates='station'
    )
    station_variables: Mapped[List['StationVariable']] = relationship(
        'StationVariable', back_populates='station'
    )

    source: Mapped['Source'] = relationship('Source', back_populates='stations')
