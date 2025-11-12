from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field


class paquete(SQLModel, table=True):
    __tablename__ = "Paquetes"
    id_paquete: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    precio: Decimal
