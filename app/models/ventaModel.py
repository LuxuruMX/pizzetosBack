from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Venta(SQLModel, table=True):
    __tablename__="Venta"
    id_venta: Optional[int] = Field(default=None, primary_key=True)
    id_suc: int = Field(foreign_key="Sucursal.id_suc")
    id_cliente: int = Field(foreign_key="Clientes.id_clie")
    fecha_hora: datetime
    total: Decimal