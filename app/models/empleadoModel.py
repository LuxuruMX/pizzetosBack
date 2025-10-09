from sqlmodel import SQLModel, Field
from typing import Optional

class Empleados(SQLModel, table=True):
    __tablename__= "Empleados"
    id_emp: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=4, max_length=120)
    direccion: str = Field(min_length=5, max_length=100)
    telefono: int = Field(ge=10000000, le=9999999999)
    id_ca: int = Field(foreign_key="Cargos.id_ca")
    id_suc: int = Field(foreign_key="Sucursal.id_suc")
    nickName: Optional[str] = None
    password: Optional[str] = None
    status: bool = Field(default=True)