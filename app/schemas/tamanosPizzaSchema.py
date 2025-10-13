from pydantic import BaseModel
from decimal import Decimal


class createTamanosPizza(BaseModel):
    tamano: str
    precio: Decimal
    
class readTamanosPizza(BaseModel):
    id_tamañop: int
    tamano: str
    precio: Decimal
    class Config:
        orm_mode = True