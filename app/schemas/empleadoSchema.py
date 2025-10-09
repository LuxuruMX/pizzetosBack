from pydantic import BaseModel, Field
from typing import Optional

class createEmpleado(BaseModel):
    nombre: str = Field(min_length=4, max_length=120)
    direccion: str = Field(min_length=5, max_length=100)
    telefono: int = Field(ge=10000000, le=9999999999)
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
        orm_mode = True