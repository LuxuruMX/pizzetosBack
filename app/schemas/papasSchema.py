from pydantic import BaseModel
from decimal import Decimal

class createPapas(BaseModel):
    orden: str
    precio: Decimal
    id_cat: int
    
class readPapas(BaseModel):
    id_papa: int
    orden: str
    precio: Decimal
    id_cat: int