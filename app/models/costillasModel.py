from typing import Optional
from sqlmodel import SQLModel, Field
from decimal import Decimal

class costillas(SQLModel, table=True):
    __tablename__ = "Costillas"
    id_cost: Optional[int] = Field(default=None, primary_key=True)
    orden: str = Field(min_length=5, max_length=100)
    precio: Decimal
    id_cat: int = Field(foreign_key="CategoriasProd.id_cat", nullable=False)