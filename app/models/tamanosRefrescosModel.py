from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric


class tamanosRefrescos(SQLModel, table=True):
    __tablename__ = "TamanosRefrescos"
    id_tamano: Optional[int] = Field(default=None, primary_key=True)
    tamano: str = Field(min_length=1, max_length=50)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))