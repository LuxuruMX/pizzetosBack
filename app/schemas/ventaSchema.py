from pydantic import BaseModel, model_validator
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from app.schemas.detallesSchema import ItemVentaRequest


class PagoVentaRequest(BaseModel):
    id_metpago: int
    monto: Decimal
    referencia: Optional[str] = None
    
    @model_validator(mode='after')
    def validar_referencia(self):
        # Convertir cadenas vacías a None
        if self.referencia is not None and self.referencia.strip() == "":
            self.referencia = None
        
        # Validar que la referencia sea obligatoria para métodos de pago 1 o 3
        if self.id_metpago in [1, 3]:
            if not self.referencia:
                raise ValueError(
                    f'Debe proporcionar una referencia cuando el método de pago es {self.id_metpago}'
                )
        return self

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
    id_cliente: Optional[int] = None
    id_direccion: Optional[int] = None  # Para tipo_servicio = 2
    mesa: Optional[int] = None  # Para tipo_servicio = 0
    total: Decimal
    comentarios: str = None
    status: int = 0
    tipo_servicio: int = 0
    nombreClie: Optional[str] = None
    id_caja: int = None
    pagos: Optional[List[PagoVentaRequest]] = None
    items: List[ItemVentaRequest]
    
    @model_validator(mode='after')
    def validar_datos(self):
        # Validar según tipo_servicio
        if self.tipo_servicio == 0:  # Comer aquí
            if self.mesa is None:
                raise ValueError('Debe especificar el número de mesa cuando tipo_servicio es 0 (comer aquí)')
        
        elif self.tipo_servicio == 2:  # Domicilio
            if self.id_cliente is None:
                raise ValueError('Debe especificar el id_cliente cuando tipo_servicio es 2 (domicilio)')
            if self.id_direccion is None:
                raise ValueError('Debe especificar el id_direccion cuando tipo_servicio es 2 (domicilio)')
        
        # Validar pagos si tipo_servicio es 1 (para llevar)
        if self.tipo_servicio == 1:
            if not self.pagos or len(self.pagos) == 0:
                raise ValueError('Debe especificar al menos un método de pago cuando tipo_servicio es 1 (para llevar)')
            
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