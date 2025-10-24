from pydantic import BaseModel
from decimal import Decimal

class priceHamburguesa(BaseModel):
    id_hamb: int
    nombre: str
    precio: Decimal
    
class PriceAlita(BaseModel):
    id_alis: int
    nombre: str
    precio: Decimal
    
class PriceCostilla(BaseModel):
    id_cos: int
    nombre: str
    precio: Decimal