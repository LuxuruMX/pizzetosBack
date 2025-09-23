from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric


class rectangular(SQLModel, table=True):
    __tablename__ = "Rectangular"
    id_rec: Optional[int] = Field(default=None, primary_key=True)
    porcion1: str = Field(min_length=5, max_length=100)
    porcion2: str = Field(min_length=5, max_length=100)
    porcion3: str = Field(min_length=5, max_length=100)
    porcion4: str = Field(min_length=5, max_length=100)
    id_esp: int = Field(foreign_key="Especialidades.id_esp", nullable=False)
    id_cat: int = Field(foreign_key="CategoriasProd.id_cat", nullable=False)