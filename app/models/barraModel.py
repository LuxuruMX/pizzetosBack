from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric

class barra(SQLModel, table=True):
    __tablename__ = "Barra"
    id_barr: Optional[int] = Field(default=None, primary_key=True)
    porcion1: str = Field(min_length=5, max_length=100)
    porcion2: str = Field(min_length=5, max_length=100)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    id_especialidad: int = Field(foreign_key="Especialidades.id_esp", nullable=False)
    id_cat: int = Field(foreign_key="CategoriasProd.id_cat", nullable=False)