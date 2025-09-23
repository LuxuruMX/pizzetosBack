from pydantic import BaseModel
from decimal import Decimal

class createTamanosRefrescos(BaseModel):
    tamano: str
    precio: Decimal
    
class readTamanosRefrescos(BaseModel):
    id_tamano: int
    tamano: str
    precio: Decimal