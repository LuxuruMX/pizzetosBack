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
    """Request completo para crear una venta"""
    id_suc: int
    id_cliente: int
    items: List[ItemVentaRequest]
    
class VentaResponse(BaseModel):
    """Response de la venta creada"""
    id_venta: int
    id_suc: int
    id_cliente: int
    fecha_hora: datetime
    total: Decimal
    detalles: List[dict]