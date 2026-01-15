from pydantic import BaseModel
from typing import Optional, List

class createDireccionNested(BaseModel):
    calle: str
    manzana: Optional[str]
    lote: Optional[str]
    colonia: Optional[str]
    referencia: Optional[str]

class createCliente(BaseModel):
    nombre: str
    apellido: str
    telefono: int
    direcciones: Optional[List[createDireccionNested]] = None
    
class readCliente(BaseModel):
    id_clie: int
    nombre: str
    apellido: str
    telefono: int
    status: bool

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
    calle: str
    manzana: Optional[str] = None
    lote: Optional[str] = None
    colonia: Optional[str] = None
    referencia: Optional[str] = None

class updateCliente(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[int] = None
    direcciones: Optional[List[updateDireccion]] = None


class onlyDireccion(BaseModel):
    id_dir: int
    calle: str
    manzana: Optional[str]
    lote: Optional[str]
    colonia: Optional[str]
    referencia: Optional[str]