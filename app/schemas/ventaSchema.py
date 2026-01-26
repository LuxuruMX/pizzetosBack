from pydantic import BaseModel, model_validator, field_validator
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict


class Ingredientes(BaseModel):
    tamano: int
    ingredientes: List[int]
    
    @field_validator('ingredientes')
    @classmethod
    def validar_ingredientes_no_vacios(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Debe seleccionar al menos un ingrediente')
        return v


class ContenidoPaquete(BaseModel):
    id_paquete: int
    id_pizzas: Optional[List[int]] = None
    id_alis: Optional[int] = None
    id_hamb: Optional[int] = None
    id_refresco: Optional[int] = 17

    @model_validator(mode='after')
    def validar_contenido_paquete(self):
        # Paquete 1: Requiere exactamente 2 pizzas
        if self.id_paquete == 1:
            if not self.id_pizzas or len(self.id_pizzas) != 2:
                raise ValueError("El Paquete 1 requiere exactamente 2 pizzas")
            if self.id_alis is not None or self.id_hamb is not None:
                raise ValueError("El Paquete 1 solo incluye pizzas y refresco")
        
        # Paquete 2: Requiere 1 pizza y (1 hamburguesa O 1 alitas), no ambas
        elif self.id_paquete == 2:
            if not self.id_pizzas or len(self.id_pizzas) != 1:
                raise ValueError("El Paquete 2 requiere exactamente 1 pizza")
            
            # Debe tener hamburguesa o alitas, pero no ambas
            if self.id_hamb is None and self.id_alis is None:
                raise ValueError("El Paquete 2 requiere 1 hamburguesa O 1 alitas")
            if self.id_hamb is not None and self.id_alis is not None:
                raise ValueError("El Paquete 2 solo puede incluir hamburguesa O alitas, no ambas")
        
        # Paquete 3: Requiere exactamente 3 pizzas
        elif self.id_paquete == 3:
            if not self.id_pizzas or len(self.id_pizzas) != 3:
                raise ValueError("El Paquete 3 requiere exactamente 3 pizzas")
            if self.id_alis is not None or self.id_hamb is not None:
                raise ValueError("El Paquete 3 solo incluye pizzas y refresco")
        
        else:
            raise ValueError(f"ID de paquete inválido: {self.id_paquete}")
        
        return self


class ItemVentaRequest(BaseModel):
    cantidad: int
    precio_unitario: Decimal
    
    id_hamb: Optional[int] = None
    id_cos: Optional[int] = None
    id_alis: Optional[int] = None
    id_spag: Optional[int] = None
    id_papa: Optional[int] = None
    id_rec: Optional[List[int]] = None
    id_barr: Optional[List[int]] = None
    id_maris: Optional[int] = None
    id_refresco: Optional[int] = None
    id_paquete: Optional[ContenidoPaquete] = None
    id_magno: Optional[List[int]] = None
    id_pizza: Optional[int] = None
    
    #datos extra para ingredientes y status
    ingredientes: Optional[Ingredientes] = None
    queso: Optional[int] = None
    
    status: Optional[int] = 1
    
    
    @field_validator('id_rec')
    @classmethod
    def validar_rec(cls, v):
        if v is not None and len(v) != 4:
            raise ValueError('id_rec debe contener exactamente 4 productos')
        return v

    @field_validator('id_barr')
    @classmethod
    def validar_barr(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('id_barr debe contener exactamente 2 productos')
        return v

    @field_validator('id_magno')
    @classmethod
    def validar_magno(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('id_magno debe contener exactamente 2 productos')
        return v



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
    
    
class VentaRequest(BaseModel):
    id_suc: int
    id_cliente: Optional[int] = None
    id_direccion: Optional[int] = None  # Para tipo_servicio = 2 y 3
    mesa: Optional[int] = None  # Para tipo_servicio = 0
    total: Decimal
    comentarios: str = None
    status: int = 0
    tipo_servicio: int = 0
    nombreClie: Optional[str] = None
    id_caja: int = None
    pagos: Optional[List[PagoVentaRequest]] = None
    items: List[ItemVentaRequest]
    fecha_entrega: Optional[datetime] = None

    @model_validator(mode='after')
    def validar_datos(self):
        # Validar según tipo_servicio
        if self.tipo_servicio == 0:  # Comer aquí
            if self.mesa is None:
                raise ValueError('Debe especificar el número de mesa cuando tipo_servicio es 0 (comer aquí)')

        elif self.tipo_servicio in [2, 3]:  # Domicilio o Pedido Especial
            if self.id_cliente is None:
                raise ValueError(f'Debe especificar el id_cliente cuando tipo_servicio es {self.tipo_servicio}')
            if self.id_direccion is None:
                raise ValueError(f'Debe especificar el id_direccion cuando tipo_servicio es {self.tipo_servicio}')

        # Validar pagos si tipo_servicio es 1 (para llevar) o 3 (pedido especial)
        if self.tipo_servicio in [1]:
            if not self.pagos or len(self.pagos) == 0:
                raise ValueError(f'Debe especificar al menos un método de pago cuando tipo_servicio es {self.tipo_servicio}')

            # Solo para 'para llevar', validar que la suma de los pagos coincida con el total
            if self.tipo_servicio == 1:
                suma_pagos = sum(pago.monto for pago in self.pagos)
                if abs(suma_pagos - self.total) > Decimal('0.01'):
                    raise ValueError(
                        f'La suma de los pagos ({suma_pagos}) debe ser igual al total de la venta ({self.total})'
                    )

            # Validar que todos los montos de pago sean positivos (aplica para 1 y 3)
            for pago in self.pagos:
                if pago.monto <= 0:
                    raise ValueError('Los montos de pago deben ser mayores a 0')
        
        # Validar items: cada item debe tener un producto O ingredientes personalizados
        for idx, item in enumerate(self.items):
            productos = [
                item.id_hamb, item.id_cos, item.id_alis, item.id_spag,
                item.id_papa, item.id_rec, item.id_barr, item.id_maris,
                item.id_refresco, item.id_paquete, item.id_magno, item.id_pizza
            ]
            def contar_producto(p):
                if p is None:
                    return 0
                if isinstance(p, list):
                    return 1 if len(p) > 0 else 0
                return 1
            
            productos = [
                item.id_hamb, item.id_cos, item.id_alis, item.id_spag,
                item.id_papa, item.id_rec, item.id_barr, item.id_maris,
                item.id_refresco, item.id_paquete, item.id_magno, item.id_pizza
            ]
            
            productos_definidos = sum(contar_producto(p) for p in productos)
            # Si hay ingredientes personalizados... (sin cambios)
            if item.ingredientes is not None:
                if productos_definidos > 0:
                    raise ValueError(f'Item {idx + 1}: No puede especificar un producto e ingredientes...')
            else:
                # AQUÍ ESTÁ EL CAMBIO:
                # Si es un paquete, permitimos más de un ID (el del paquete + sus contenidos)
                if item.id_paquete is not None:
                    # Validar que al menos haya 1 producto (el paquete en sí ya cuenta)
                    if productos_definidos < 1:
                         raise ValueError(f'Item {idx + 1}: Paquete inválido')
                else:
                    # Si NO es paquete, mantenemos la regla estricta de SOLO UNO
                    if productos_definidos != 1:
                        raise ValueError(
                            f'Item {idx + 1}: Debe especificar exactamente un producto o ingredientes personalizados'
                        )
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


# Schema para recrear ticket/pedido
class ItemRecreaTicketRequest(BaseModel):
    cantidad: int
    nombre: str
    tamano: Optional[str] = None
    tipo: str  # "Pizza", "Hamburguesa", "Alitas", etc.
    precio_base: Decimal  # Precio sin extras
    precio_extra: Decimal = Decimal("0.00")  # Costo total de extras
    precioUnitario: Decimal  # Precio total (Base + Extra)
    conQueso: Optional[bool] = False
    
    # Campos opcionales para paquetes y productos especiales
    id_paquete: Optional[int] = None
    id_rec: Optional[List[int]] = None  # Para rectangular
    id_barr: Optional[List[int]] = None  # Para barra


class RecreaTicketRequest(BaseModel):
    productos: List[ItemRecreaTicketRequest]
    
    @field_validator('productos')
    @classmethod
    def validar_productos(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Debe especificar al menos un producto')
        return v


class RecreaTicketResponse(BaseModel):
    status: str
    mensaje: str
    productos_procesados: int
    total_calculado: Decimal
    detalles: List[Dict]


