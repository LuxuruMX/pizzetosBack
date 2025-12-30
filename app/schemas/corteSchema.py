from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from decimal import Decimal


class EventoCaja(BaseModel):
    tipo: str
    fecha: datetime
    observaciones: Optional[str]

class TransaccionDetalle(BaseModel):
    id_venta: int
    fecha: datetime
    id_metpago: int
    referencia: Optional[str]
    monto: Decimal
    sucursal: Optional[str] = None
    eventos_caja: Optional[List[EventoCaja]] = None
    notas: Optional[str] = None
class ResumenDia(BaseModel):
    dia: int
    efectivo: Decimal
    tarjeta: Decimal
    transferencia: Decimal

class CajaDiaDetalle(BaseModel):
    id_caja: int
    empleado: str
    hora_apertura: datetime
    hora_cierre: Optional[datetime]
    observaciones_apertura: Optional[str]
    observaciones_cierre: Optional[str]

class PagoVentaDetalle(BaseModel):
    id_venta: int
    dia: int
    metodo_pago: str
    referencia: Optional[str]
    monto: Decimal
    id_caja: int

class SucursalDiaDetalle(BaseModel):
    sucursal: str
    cajas: List[CajaDiaDetalle]
    pagos: List[PagoVentaDetalle]