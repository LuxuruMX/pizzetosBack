from pydantic import BaseModel
from decimal import Decimal

class createPaquete1(BaseModel):
    id_especialidad: int
    id_refresco: int
    precio: Decimal
    
class readPaquete1(BaseModel):
    id_paquete1: int
    id_especialidad: int
    id_refresco: int
    precio: Decimal
    
    
class createPaquete2(BaseModel):
    id_especialidad: int
    id_alitas: int
    id_hamburguesa: int
    id_refresco: int
    precio: Decimal
    
class readPaquete2(BaseModel):
    id_paquete2: int
    id_especialidad: int
    id_alitas: int
    id_hamburguesa: int
    id_refresco: int
    precio: Decimal
    
    
class createPaquete3(BaseModel):
    id_especialidad: int
    id_refresco: int
    precio: Decimal
    
class readPaquete3(BaseModel):
    id_paquete3: int
    id_especialidad: int
    id_refresco: int
    precio: Decimal