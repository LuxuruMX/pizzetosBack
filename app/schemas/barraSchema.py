from pydantic import BaseModel, Field
from decimal import Decimal


class createBarra(BaseModel):
    porcion1: str
    porcion2: str
    id_especialidad: int
    id_cat: int
    
class readBarra(BaseModel):
    id_barr: int
    porcion1: str
    porcion2: str
    id_especialidad: int
    id_cat: int
    precio: Decimal

    class Config:
        orm_mode = True
    