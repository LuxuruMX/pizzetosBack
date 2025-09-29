from pydantic import BaseModel
from decimal import Decimal

class createMagno(BaseModel):
    id_especialidad: int
    id_refresco: int
    precio: Decimal
    
class readMagno(BaseModel):
    id_magno: int
    id_especialidad: int
    id_refresco: int
    precio: Decimal
    
class readMagnoOut(BaseModel):
    id_magno: int
    especialidad: str
    refresco: str
    precio: Decimal