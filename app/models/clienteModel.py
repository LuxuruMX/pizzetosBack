from sqlmodel import SQLModel, Field
from typing import Optional


class Cliente(SQLModel, table=True):
    __tablename__="Clientes"
    id_clie: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=3, max_length=100)
    telefono: int = Field(ge=10000000, le=9999999999)
    
class direccion(SQLModel, table=True):
    __tablename__="Direcciones"
    id_dir: Optional[int] = Field(default=None, primary_key=True)
    id_clie: int
    calle: str = Field(min_length=5, max_length=255)
    manzana: Optional[str] = Field(default=None, max_length=10)
    lote: Optional[str] = Field(default=None, max_length=10)
    colonia: Optional[str] = Field(default=None, max_length=100)
    referencia: Optional[str] = Field(default=None, max_length=255)