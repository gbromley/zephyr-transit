import datetime as dt
from typing import List
from .base import Base
from sqlalchemy import String, REAL, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship



class Source(Base):
    __tablename__="sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    api_endpoint: Mapped[str] = mapped_column(String, nullable=False)
    
    stations: Mapped[List["Station"]] = relationship("Station", back_populates="source")
