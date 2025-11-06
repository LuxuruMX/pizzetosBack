from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class createDetalleVenta(BaseModel):
    id_venta: int
    cantidad: Decimal
    precio_unitario: Decimal

    id_hamb: Optional[int] = None
    id_cos: Optional[int] = None
    id_alis: Optional[int] = None
    id_spag: Optional[int] = None
    id_papa: Optional[int] = None
    id_rec: Optional[int] = None
    id_barr: Optional[int] = None
    id_maris: Optional[int] = None
    id_refresco: Optional[int] = None
    id_paquete: Optional[int] = None
    id_paquete2: Optional[int] = None
    id_paquete3: Optional[int] = None
    id_magno: Optional[int] = None
    id_pizza: Optional[int] = None

class readDetalleVenta(BaseModel):
    id_detalle: int
    id_venta: int
    cantidad: Decimal
    precio_unitario: Decimal

    id_hamb: Optional[int]
    id_cos: Optional[int]
    id_alis: Optional[int]
    id_spag: Optional[int]
    id_papa: Optional[int]
    id_rec: Optional[int]
    id_barr: Optional[int]
    id_maris: Optional[int]
    id_refresco: Optional[int]
    id_paquete: Optional[int]
    id_paquete2: Optional[int]
    id_paquete3: Optional[int]
    id_magno: Optional[int]
    id_pizza: Optional[int] = None



class ItemVentaRequest(BaseModel):
    cantidad: int
    precio_unitario: Decimal
    
    id_hamb: Optional[int] = None
    id_cos: Optional[int] = None
    id_alis: Optional[int] = None
    id_spag: Optional[int] = None
    id_papa: Optional[int] = None
    id_rec: Optional[int] = None
    id_barr: Optional[int] = None
    id_maris: Optional[int] = None
    id_refresco: Optional[int] = None
    id_paquete1: Optional[int] = None
    id_paquete2: Optional[int] = None
    id_paquete3: Optional[int] = None
    id_magno: Optional[int] = None
    id_pizza: Optional[int] = None