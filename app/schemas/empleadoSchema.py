from pydantic import BaseModel, Field

class createEmpleado(BaseModel):
    nombre: str = Field(min_length=10, max_length=120)
    direccion: str = Field(min_length=5, max_length=100)
    telefono: int = Field(ge=10000000, le=9999999999)
    id_ca: int
    id_suc: int

class readEmpleado(BaseModel):
    id_emp: int
    nombre: str
    direccion: str
    telefono: int
    id_ca: int
    id_suc: int