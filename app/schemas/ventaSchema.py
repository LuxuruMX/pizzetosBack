from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class createVenta(BaseModel):
    id_suc: int
    id_cliente: int
    total: Decimal


class readVenta(BaseModel):
    id_venta: int
    id_suc: int
    id_cliente: int
    fecha_hora: datetime
    total: Decimal