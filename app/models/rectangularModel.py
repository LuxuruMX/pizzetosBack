from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric


class rectangular(SQLModel, table=True):
    __tablename__ = "Rectangular"
    id_rec: Optional[int] = Field(default=None, primary_key=True)
    id_esp: int = Field(foreign_key="Especialidades.id_esp", nullable=False)
    id_cat: int = Field(foreign_key="CategoriasProd.id_cat", nullable=False)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))