from datetime import datetime

from sqlalchemy import REAL, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Observation(Base):
    """Weather observation data point."""

    __tablename__ = 'observations'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    station_id: Mapped[int] = mapped_column(ForeignKey('stations.id'), index=True)
    variable_id: Mapped[int] = mapped_column(ForeignKey('variables.id'), index=True)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    value: Mapped[float] = mapped_column(REAL, nullable=True)

    station: Mapped['Station'] = relationship('Station', back_populates='observations')
    variable: Mapped['Variable'] = relationship('Variable', back_populates='observations')

    __table_args__ = (UniqueConstraint('station_id', 'variable_id','time', name='unique_observation'),
        )
