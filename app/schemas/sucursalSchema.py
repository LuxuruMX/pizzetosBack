from pydantic import BaseModel, Field


class createSucursal(BaseModel):
    nombre: str = Field(min_length=5, max_length=20)
    direccion: str = Field(min_length=5, max_length=100)
    telefono: int = Field(ge=10000000, le=9999999999)

class readSucursal(BaseModel):
    id_suc: int
    nombre: str
    direccion: str
    telefono: int
