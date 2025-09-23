from pydantic import BaseModel
from decimal import Decimal


class createRectangular(BaseModel):
    porcion1: str
    porcion2: str
    porcion3: str
    porcion4: str
    id_esp: int
    id_cat: int
    
    
class readRectangular(BaseModel):
    id_rec: int
    porcion1: str
    porcion2: str
    porcion3: str
    porcion4: str
    id_esp: int
    id_cat: int