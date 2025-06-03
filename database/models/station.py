import datetime as dt
from typing import List
from .base import Base
from sqlalchemy import BigInteger, REAL, ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Station(Base):
    __table_name__="stations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(REAL, nullable=False)
    longitude: Mapped[float] = mapped_column(REAL, nullable=False)
    elevation: Mapped[float] = mapped_column(REAL, nullable=True)
    road_name: Mapped[str] = mapped_column(String)
    road_direction: Mapped[str] = mapped_column(String)


    observations: Mapped[List["Observation"]] = relationship("Observation", back_populates="station")
    station_variables: Mapped[List["StationVariable"]] = relationship("StationVariable", back_populates="station")

