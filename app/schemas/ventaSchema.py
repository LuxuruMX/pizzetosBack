from pydantic import BaseModel, model_validator
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from app.schemas.detallesSchema import ItemVentaRequest


class PagoVentaRequest(BaseModel):
    id_metpago: int
    monto: Decimal

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
    tipo_servicio: int = 0
    pagos: Optional[List[PagoVentaRequest]] = None
    items: List[ItemVentaRequest]
    
    @model_validator(mode='after')
    def validar_pagos(self):
        # Si tipo_servicio es 1, los pagos son obligatorios
        if self.tipo_servicio == 1:
            if not self.pagos or len(self.pagos) == 0:
                raise ValueError('Debe especificar al menos un método de pago cuando tipo_servicio es 1')
            
            # Validar que la suma de los pagos coincida con el total
            suma_pagos = sum(pago.monto for pago in self.pagos)
            if abs(suma_pagos - self.total) > Decimal('0.01'):  # Tolerancia de 1 centavo por redondeo
                raise ValueError(
                    f'La suma de los pagos ({suma_pagos}) debe ser igual al total de la venta ({self.total})'
                )
            
            # Validar que todos los montos sean positivos
            for pago in self.pagos:
                if pago.monto <= 0:
                    raise ValueError('Los montos de pago deben ser mayores a 0')
        
        return self

    
class VentaResponse(BaseModel):
    id_venta: int
    id_suc: int
    id_cliente: int
    fecha_hora: datetime
    total: Decimal
    detalles: List[dict]



class RegistrarPagoRequest(BaseModel):
    id_venta: int
    pagos: List[PagoVentaRequest]
    
    @model_validator(mode='after')
    def validar_pagos(self):
        if not self.pagos or len(self.pagos) == 0:
            raise ValueError('Debe especificar al menos un método de pago')
        
        # Validar que todos los montos sean positivos
        for pago in self.pagos:
            if pago.monto <= 0:
                raise ValueError('Los montos de pago deben ser mayores a 0')
        
        return self