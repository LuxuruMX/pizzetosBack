from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class Empleados(SQLModel, table=True):
    __tablename__ = "Venta"
    id_venta: Optional[int] = Field(default=None, primary_key=True)
    id_sucursal: int = Field(foreign_key="id_suc")
    id_cliente: int = Field(foreign_key="id_cliente")
    fecha_hora: datetime
    total: Decimal