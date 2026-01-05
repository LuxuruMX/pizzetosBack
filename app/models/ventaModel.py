from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy import JSON



class Venta(SQLModel, table=True):
    __tablename__ = "Venta"
    
    id_venta: Optional[int] = Field(default=None, primary_key=True)
    id_suc: int = Field(foreign_key="Sucursal.id_suc")
    mesa: Optional[int] = Field(default=None)
    fecha_hora: datetime
    total: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    status: Optional[int] = Field(default=0)
    comentarios: Optional[str] = Field(default=None)
    tipo_servicio: Optional[int] = Field(default=0)
    nombreClie: Optional[str] = Field(default=None)
    id_caja: int = Field(default=None, foreign_key="Caja.id_caja")
    detalles: Optional[str] = Field(default=None)
    ingredientes: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON)
    )


class Ingredientes(SQLModel, table=True):
    __tablename__ = "Ingredientes"
    id_ingrediente: Optional[int] = Field(default=None, primary_key=True)
    ingrediente: str = Field(min_length=2, max_length=100)