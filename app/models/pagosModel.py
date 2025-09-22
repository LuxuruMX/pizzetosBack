from sqlmodel import SQLModel, Field
from typing import Optional
from decimal import Decimal

class Pago(SQLModel, table=True):
    __tablename__="Pago"
    id_pago: Optional[int] = Field(default=None, primary_key=True)
    id_venta:int
    id_metpago: int
    monto: Decimal