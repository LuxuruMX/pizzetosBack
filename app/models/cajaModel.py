from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from typing import Optional
from datetime import datetime
from decimal import Decimal



class Caja(SQLModel, table=True):
    __tablename__ = "Caja"
    
    id_caja: Optional[int] = Field(default=None, primary_key=True)
    id_suc: int = Field(foreign_key="Sucursal.id_suc")
    id_emp: int = Field(foreign_key="Empleados.id_emp")
    fecha_apertura: datetime
    fecha_cierre: Optional[datetime] = Field(default=None)
    monto_inicial: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    monto_final: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2), nullable=True))
    status: Optional[int] = Field(default=0)
    observaciones_apertura: Optional[str] = Field(default=None)
    observaciones_cierre: Optional[str] = Field(default=None)