from pydantic import BaseModel
from decimal import Decimal


class createHamburguesas(BaseModel):
    paquete: str
    precio: Decimal
    id_cat: int
    
class readHamburguesas(BaseModel):
    id_hamb: int
    paquete: str
    precio: Decimal
    id_cat: int