from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric

class hamburguesas(SQLModel, table=True):
    __tablename__ = "Hamburguesas"
    id_hamb: Optional[int] = Field(default=None, primary_key=True)
    paquete: str = Field(min_length=5, max_length=100)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    id_cat: int = Field(foreign_key="CategoriasProd.id_cat", nullable=False)