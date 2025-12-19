from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class PEspecial(SQLModel, table=True):
    __tablename__ = "PEspeciales"
    id_pespeciales: Optional[int] = Field(default=None, primary_key=True)
    id_venta: int = Field(foreign_key="Venta.id_venta")
    id_dir: int = Field(foreign_key="Direcciones.id_dir")
    id_clie: int = Field(foreign_key="Clientes.id_clie")
    fecha_creacion: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime, server_default=func.now(), nullable=False),
    )
    fecha_entrega: Optional[datetime] = Field(default=None)
    status: Optional[int] = Field(default=1)