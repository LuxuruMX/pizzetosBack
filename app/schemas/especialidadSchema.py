from pydantic import BaseModel
from decimal import Decimal


class createEspecialidad(BaseModel):
    nombre: str
    descripcion: str
    
class readEspecialidad(BaseModel):
    id_esp: int
    nombre: str
    descripcion: str