from pydantic import BaseModel
from decimal import Decimal


class createRectangular(BaseModel):
    id_esp: int
    id_cat: int
    
    
class readRectangular(BaseModel):
    id_rec: int
    id_esp: int
    id_cat: int
    
class readRectangularOut(BaseModel):
    id_rec: int
    especialidad: str
    categoria: str