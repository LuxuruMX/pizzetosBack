from pydantic import BaseModel, Field
from decimal import Decimal


class createCostillas(BaseModel):
    orden: str
    precio: Decimal
    id_cat: int
    
    
class readCostillas(BaseModel):
    id_cos: int
    orden: str
    precio: Decimal
    id_cat: int

    class Config:
        from_attributes = True
        
class readCostillasOut(BaseModel):
    id_cos: int
    orden: str
    precio: Decimal
    categoria: str