from __future__ import annotations
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric


class DetalleVenta(SQLModel, table=True):
    __tablename__ = "DetalleVenta"
    
    id_detalle: Optional[int] = Field(default=None, primary_key=True)
    id_venta: int = Field(foreign_key="Venta.id_venta")
    
    cantidad: int = Field(nullable=False)
    precio_unitario: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False)
    )
    
    id_hamb: Optional[int] = Field(default=None)
    id_cos: Optional[int] = Field(default=None)
    id_alis: Optional[int] = Field(default=None)
    id_spag: Optional[int] = Field(default=None)
    id_papa: Optional[int] = Field(default=None)
    id_rec: Optional[int] = Field(default=None)
    id_barr: Optional[int] = Field(default=None)
    id_maris: Optional[int] = Field(default=None)
    id_refresco: Optional[int] = Field(default=None)
    id_paquete1: Optional[int] = Field(default=None)
    id_paquete2: Optional[int] = Field(default=None)
    id_paquete3: Optional[int] = Field(default=None)
    id_magno: Optional[int] = Field(default=None)
    
