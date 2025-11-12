from pydantic import BaseModel
from decimal import Decimal

class readPaquete1(BaseModel):
    id_paquete: int
    nombre: str
    descripcion: str
    precio: Decimal
