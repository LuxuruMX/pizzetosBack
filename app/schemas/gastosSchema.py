from pydantic import BaseModel, Field
from decimal import Decimal


class createGastos(BaseModel):
    id_suc: int
    nombre: str = Field(min_length=3, max_length=255)
    precio: Decimal


class readGastos(BaseModel):
    id_gastos: int
    id_suc: int
    nombre: str
    precio: Decimal
