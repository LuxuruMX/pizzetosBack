from sqlmodel import SQLModel, Field
from typing import Optional
from decimal import Decimal

class Gastos(SQLModel, table=True):
    __tablename__="Gastos"
    id_gastos: Optional[int] = Field(default=None, primary_key=True)
    id_suc: int
    nombre: str = Field(min_length=3, max_length=255)
    precio: Decimal