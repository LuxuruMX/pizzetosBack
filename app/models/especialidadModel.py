from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric


class especialidad(SQLModel, table=True):
    __tablename__ = "Especialidades"
    id_esp: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=3, max_length=50)
    descripcion: str = Field(min_length=5, max_length=200)