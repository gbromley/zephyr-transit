from typing import List

from sqlalchemy import REAL, BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class StationVariable(Base):

    __tablename__ = 'station_variables'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"))
    variable_id: Mapped[int] = mapped_column(ForeignKey("variables.id"))

    station: Mapped['Station'] = relationship('Station', back_populates='station_variables')
    variable: Mapped['Variable'] = relationship('Variable', back_populates='station_variables')
