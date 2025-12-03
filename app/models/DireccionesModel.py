from sqlmodel import SQLModel, Field
from typing import Optional



class Direccion(SQLModel, table=True):
    __tablename__ = "Direcciones"
    
    id_dir: Optional[int] = Field(default=None, primary_key=True)
    id_clie: int = Field(foreign_key="Clientes.id_clie")
    calle: str
    manzana: Optional[str]
    lote: Optional[str]
    colonia: Optional[str]
    referencia: Optional[str] = Field(default=None)