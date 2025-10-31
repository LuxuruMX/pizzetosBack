from pydantic import BaseModel, Field
from typing import Optional, List

class createDireccionNested(BaseModel):
    calle: str = Field(min_length=5, max_length=255)
    manzana: Optional[str] = Field(default=None, max_length=10)
    lote: Optional[str] = Field(default=None, max_length=10)
    colonia: Optional[str] = Field(default=None, max_length=100)
    referencia: Optional[str] = Field(default=None, max_length=255)

class createCliente(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    apellido: str = Field(min_length=3, max_length=100)
    telefono: int = Field(ge=10000000, le=9999999999)
    direcciones: Optional[List[createDireccionNested]] = None
    
class readCliente(BaseModel):
    id_clie: int
    nombre: str
    apellido: str
    telefono: int

class readClientePOS(BaseModel):
    id_clie: int
    nombre: str

class readDireccion(BaseModel):
    id_dir: int
    id_clie: int
    calle: str
    manzana: Optional[str]
    lote: Optional[str]
    colonia: Optional[str]
    referencia: Optional[str]

class DireccionResponse(BaseModel):
    id_dir: int
    calle: str
    manzana: Optional[str]
    lote: Optional[str]
    colonia: Optional[str]
    referencia: Optional[str]

class ClienteConDirecciones(BaseModel):
    id_clie: int
    nombre: str
    apellido: str
    telefono: int
    direcciones: List[DireccionResponse] = []

class updateDireccion(BaseModel):
    id_dir: Optional[int] = None  # Si tiene id_dir, actualiza; si no, crea nueva
    calle: str = Field(min_length=5, max_length=255)
    manzana: Optional[str] = Field(default=None, max_length=10)
    lote: Optional[str] = Field(default=None, max_length=10)
    colonia: Optional[str] = Field(default=None, max_length=100)
    referencia: Optional[str] = Field(default=None, max_length=255)

class updateCliente(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(default=None, min_length=3, max_length=100)
    telefono: Optional[int] = Field(default=None, ge=10000000, le=9999999999)
    direcciones: Optional[List[updateDireccion]] = None