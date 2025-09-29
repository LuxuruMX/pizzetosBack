from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric


class magno(SQLModel, table=True):
    __tablename__ = "Magno"
    id_magno: Optional[int] = Field(default=None, primary_key=True)
    id_especialidad: int = Field(foreign_key="Especialidades.id_esp", nullable=False)
    id_refresco: int = Field(foreign_key="Refrescos.id_refresco", nullable=False)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    