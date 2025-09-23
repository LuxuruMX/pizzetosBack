from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric


class refrescos(SQLModel, table=True):
    __tablename__ = "Refrescos"
    id_refresco: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=3, max_length=50)
    id_tamano: int = Field(foreign_key="TamanosRefrescos.id_tamano", nullable=False)
    id_cat: int = Field(foreign_key="CategoriasProd.id_cat", nullable=False)