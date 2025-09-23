from pydantic import BaseModel
from decimal import Decimal

class createRefrescos(BaseModel):
    nombre: str
    id_tamano: int
    id_cat: int
    
class readRefrescos(BaseModel):
    id_refresco: int
    nombre: str
    id_tamano: int
    id_cat: int