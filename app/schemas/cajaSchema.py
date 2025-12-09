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



class FlujoCajaResponse(BaseModel):
    id_caja: int
    fecha_apertura: datetime
    fecha_cierre: Optional[datetime]
    monto_inicial: Decimal
    ventas_efectivo: Decimal
    ventas_tarjeta: Decimal
    ventas_transferencia: Decimal
    total_ventas: Decimal
    movimientos_extra: Decimal  # ingresos - egresos
    monto_esperado: Decimal
    monto_final: Optional[Decimal]
    diferencia: Optional[Decimal]
    status: int
    nombre_usuario: str