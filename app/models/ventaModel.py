from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Numeric
from typing import Optional
from datetime import datetime
from decimal import Decimal



class Venta(SQLModel, table=True):
    __tablename__ = "Venta"
    
    id_venta: Optional[int] = Field(default=None, primary_key=True)
    id_suc: int = Field(foreign_key="Sucursal.id_suc")
    id_cliente: int = Field(foreign_key="Clientes.id_clie")
    fecha_hora: datetime
    total: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    status: Optional[int] = Field(default=0)
    comentarios: Optional[str] = Field(default=None)