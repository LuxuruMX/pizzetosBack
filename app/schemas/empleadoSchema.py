from pydantic import BaseModel, Field
from typing import Optional

class createEmpleado(BaseModel):
    nombre: str
    direccion: str
    telefono: int
    id_ca: int
    id_suc: int
    nickName: Optional[str] = None
    password: Optional[str] = None
    status: bool = Field(default=True)


class readEmpleadoNoPass(BaseModel):
    id_emp: int
    nombre: str
    direccion: str
    telefono: int
    cargo: str
    sucursal: str
    nickName: str
    status: bool
    class Config:
        from_attributes = True