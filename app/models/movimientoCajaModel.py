from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from typing import Optional
from datetime import datetime
from decimal import Decimal

class MovimientoCaja(SQLModel, table=True):
    __tablename__ = "MovimientosCaja"
    
    id_movimiento: Optional[int] = Field(default=None, primary_key=True)
    id_caja: int = Field(foreign_key="Caja.id_caja")
    tipo_movimiento: str  # 1: Ingreso, 2: Egreso, 3: Retiro
    monto: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    concepto: str
    fecha_hora: datetime