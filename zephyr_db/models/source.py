from typing import List

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Source(Base):
    """A DOT data source."""

    __tablename__ = 'sources'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    api_endpoint: Mapped[str] = mapped_column(String, nullable=False)

    stations: Mapped[List['Station']] = relationship('Station', back_populates='source')
