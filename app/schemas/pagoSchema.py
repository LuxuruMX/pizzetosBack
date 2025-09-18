from pydantic import BaseModel
from decimal import Decimal


class createPagos(BaseModel):
    id_venta:int
    id_metpago: int
    monto: Decimal


class readPagos(BaseModel):
    id_pago: int
    id_venta:int
    id_metpago: int
    monto: Decimal