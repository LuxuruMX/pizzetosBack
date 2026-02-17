from pydantic import BaseModel, Field


class createSucursal(BaseModel):
    nombre: str = Field(min_length=2, max_length=40)
    direccion: str = Field(min_length=2, max_length=100)
    telefono: int

class readSucursal(BaseModel):
    id_suc: int
    nombre: str
    direccion: str
    telefono: int
