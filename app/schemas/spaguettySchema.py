from pydantic import BaseModel
from decimal import Decimal

class createSpaguetty(BaseModel):
    orden: str
    precio: Decimal
    id_cat: int
    
class readSpaguetty(BaseModel):
    id_spag: int
    orden: str
    precio: Decimal
    id_cat: int