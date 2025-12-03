from sqlmodel import SQLModel, Field
from typing import Optional


class Cliente(SQLModel, table=True):
    __tablename__="Clientes"
    id_clie: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=3, max_length=100)
    telefono: int = Field(ge=10000000, le=9999999999)
    