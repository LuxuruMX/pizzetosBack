from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional




class AperturaCajaRequest(BaseModel):
    id_suc: int
    id_emp: int
    monto_inicial: Decimal
    observaciones_apertura: Optional[str] = None



class CierreCajaRequest(BaseModel):
    monto_final: Decimal
    observaciones_cierre: Optional[str] = None



class MovimientoCajaRequest(BaseModel):
    tipo_movimiento: str  # 'ingreso', 'egreso', 'retiro'
    monto: Decimal
    concepto: str



class CajaDetalleResponse(BaseModel):
    id_caja: int
    fecha_apertura: datetime
    estado: str  # "abierta", "cerrada"
    usuario_apertura: str
    monto_inicial: float
    total_ventas: float
    numero_ventas: int
    total_efectivo: float
    total_tarjeta: float
    total_transferencia: float