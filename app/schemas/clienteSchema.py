from pydantic import BaseModel, Field


class createCliente(BaseModel):
    nombre: str = Field(min_length=3, max_length=100)
    apellido: str = Field(min_length=3, max_length=100)
    direccion: str = Field(min_length=5, max_length=255)
    telefono: str = Field(ge=10000000, le=9999999999)
    
    

class readCliente(BaseModel):
    id_cliente: int
    nombre: str
    apellido: str
    direccion: str
    telefono: str
