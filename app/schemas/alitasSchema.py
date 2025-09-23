from pydantic import BaseModel
from decimal import Decimal

class createAlitas(BaseModel):
    orden: str
    precio: Decimal
    id_cat: int
    
    
class readAlitas(BaseModel):
    id_alis: int
    orden: str
    precio: Decimal
    id_cat: int