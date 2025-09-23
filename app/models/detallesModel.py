from __future__ import annotations
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric



class DetalleVenta(SQLModel, table=True):
    __tablename__ = "DetalleVenta"
    id_detalle: Optional[int] = Field(default=None, primary_key=True)

    # FK a ventas.id_venta (ajusta el nombre si tu tabla/columna real difiere)
    id_venta: int = Field(    )

    # Campos obligatorios
    cantidad: int = Field(nullable=False)
    precio_un: Decimal = Field(
        sa_column=Column(Numeric(10, 2), nullable=False)
    )

    # Campos opcionales (NULL)
    id_hamb: Optional[int] = None
    id_cos: Optional[int] = None
    id_alis: Optional[int] = None
    id_spag: Optional[int] = None
    id_papa: Optional[int] = None
    id_rec: Optional[int] = None
    id_barr: Optional[int] = None
    id_maris: Optional[int] = None
    id_refresc: Optional[int] = None
    id_paquete1: Optional[int] = None
    id_paquete2: Optional[int] = None
    id_paquete3: Optional[int] = None
    id_magno: Optional[int] = None
