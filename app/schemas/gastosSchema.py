from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class createGastos(BaseModel):
    id_suc: int
    descripcion: str = Field(min_length=3, max_length=255)
    precio: Decimal
    id_caja: int


class readGastos(BaseModel):
    id_gastos: int
    descripcion: str
    precio: Decimal
    fecha: datetime
    class Config:
        from_attributes = True


class readGastoNoFecha(BaseModel):
    id_gastos: int
    descripcion: str
    precio: Decimal
    class Config:
        from_attributes = True

class modGastos(BaseModel):
    descripcion: str = Field(min_length=3, max_length=255)
    precio: Decimal