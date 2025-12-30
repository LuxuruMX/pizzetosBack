from sqlmodel import SQLModel, Field
from typing import Optional



class pDireccion(SQLModel, table=True):
    __tablename__ = "PDomicilio"
    
    id_pdomicilio: Optional[int] = Field(default=None, primary_key=True)
    id_clie: int = Field(foreign_key="Clientes.id_clie")
    id_dir: int = Field(foreign_key="Direcciones.id_dir")
    id_venta: int = Field(foreign_key="Venta.id_venta")
    status: Optional[int] = Field(default=1)
    detalles: Optional[str] = Field(default=None)