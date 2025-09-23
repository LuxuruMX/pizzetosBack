from pydantic import BaseModel
from decimal import Decimal


class createMariscos(BaseModel):
    nombre: str
    descripcion: str
    id_tamañop: int
    id_cat: int
    
class readMariscos(BaseModel):
    id_maris: int
    nombre: str
    descripcion: str
    id_tamañop: int
    id_cat: int