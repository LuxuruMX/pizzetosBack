from sqlmodel import SQLModel, Field
from typing import Optional


class Cliente(SQLModel, table=True):
    __tablename__="Clientes"
    id_clie: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    telefono: int
    status: Optional[bool] = Field(default=True)

