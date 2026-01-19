from __future__ import annotations
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric
from sqlalchemy import JSON


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
    id_rec: Optional[List[int]] = Field(
        sa_column=Column(JSON)
    )
    id_barr: Optional[List[int]] = Field(
        sa_column=Column(JSON)
    )
    id_maris: Optional[int] = Field(default=None)
    id_refresco: Optional[int] = Field(default=None)
    id_paquete: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSON)
    )
    id_magno: Optional[List[int]] = Field(
        sa_column=Column(JSON)
    )
    id_pizza: Optional[int] = Field(default=None)
    ingredientes: Optional[Dict[str, Any]] = Field(
        sa_column=Column(JSON)
    )
    queso: Optional[int] = Field(default=None)
    status: Optional[int] = Field(default=1)
    
    
