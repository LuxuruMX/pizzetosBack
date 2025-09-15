from sqlmodel import SQLModel, Field
from typing import Optional

class Sucursal(SQLModel, table=True):
    __tablename__ = "Sucursal"
    id_suc: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=5, max_length=20)
    direccion: str = Field(min_length=5, max_length=100)
    telefono: int = Field(ge=10000000, le=9999999999)