from pydantic import BaseModel, Field
from decimal import Decimal


class createBarra(BaseModel):
    id_especialidad: int
    id_cat: int
    precio: Decimal
    
class readBarra(BaseModel):
    id_barr: int
    id_especialidad: int
    id_cat: int
    precio: Decimal

    class Config:
        from_attributes = True
    
class readBarraOut(BaseModel):
    id_barr: int
    especialidad: str
    categoria: str
    precio: Decimal

    class Config:
        from_attributes = True