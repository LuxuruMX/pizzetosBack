from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import List
from app.schemas.detallesSchema import ItemVentaRequest


class createVenta(BaseModel):
    id_suc: int
    id_cliente: int


class readVenta(BaseModel):
    id_venta: int
    id_suc: int
    id_cliente: int
    fecha_hora: datetime
    total: Decimal
    status:int
    
    
class VentaRequest(BaseModel):
    id_suc: int
    id_cliente: int
    total: Decimal
    comentarios: str = None
    status: int = 1
    items: List[ItemVentaRequest]
    
class VentaResponse(BaseModel):
    id_venta: int
    id_suc: int
    id_cliente: int
    fecha_hora: datetime
    total: Decimal
    detalles: List[dict]