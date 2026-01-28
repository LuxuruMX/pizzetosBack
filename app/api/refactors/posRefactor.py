from fastapi import HTTPException
from sqlmodel import Session
from decimal import Decimal
from datetime import datetime

from app.models.ventaModel import Venta
from app.models.pDireccionModel import pDireccion
from app.models.pEspecialModel import PEspecial
from app.models.pagosModel import Pago
from app.models.detallesModel import DetalleVenta
from app.models.clienteModel import Cliente
from app.models.sucursalModel import Sucursal
from app.models.DireccionesModel import Direccion



def validar_items(venta_request):
    """Valida que la venta tenga al menos un item"""
    if not venta_request.items:
        raise HTTPException(
            status_code=400, 
            detail="La venta debe contener al menos un item"
        )

def validar_pagos_tipo_servicio(venta_request):
    """Valida que existan pagos para tipos de servicio que los requieren"""
    if venta_request.tipo_servicio in [1]:
        if not venta_request.pagos or len(venta_request.pagos) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Debe especificar al menos un método de pago cuando el tipo de servicio es {venta_request.tipo_servicio}"
            )

def validar_cliente_direccion(venta_request, session: Session):
    """Valida cliente y dirección para tipos de servicio que los requieren"""
    if venta_request.tipo_servicio not in [2, 3]:
        return None, None
    
    if not venta_request.id_cliente:
        raise HTTPException(
            status_code=400,
            detail=f"Debe especificar el id_cliente cuando el tipo de servicio es {venta_request.tipo_servicio}"
        )

    cliente = session.get(Cliente, venta_request.id_cliente)
    if not cliente:
        raise HTTPException(
            status_code=404,
            detail=f"Cliente con ID {venta_request.id_cliente} no encontrado"
        )

    if not venta_request.id_direccion:
        raise HTTPException(
            status_code=400,
            detail=f"Debe especificar el id_direccion cuando el tipo de servicio es {venta_request.tipo_servicio}"
        )

    direccion = session.get(Direccion, venta_request.id_direccion)
    if not direccion:
        raise HTTPException(
            status_code=404,
            detail=f"Dirección con ID {venta_request.id_direccion} no encontrada"
        )
    
    return cliente, direccion

def validar_domicilio(venta_request):
    """Valida y procesa información específica de domicilio"""
    if venta_request.tipo_servicio != 2:
        return None
    
    if not venta_request.pagos or len(venta_request.pagos) == 0:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar el método de pago para domicilio"
        )
    
    pago = venta_request.pagos[0]
    
    # Transferencia (id_metpago == 1)
    if pago.id_metpago == 1:
        if not pago.referencia:
            raise HTTPException(
                status_code=400, 
                detail="Debe proporcionar la referencia de la transferencia"
            )
        if abs(pago.monto - venta_request.total) > Decimal('0.01'):
            raise HTTPException(
                status_code=400, 
                detail="El monto de la transferencia debe ser igual al total"
            )
        return "Pago realizado por transferencia"
    
    # Tarjeta (id_metpago == 2)
    elif pago.id_metpago == 2:
        return "Llevar terminal"
    
    # Efectivo (id_metpago == 3)
    elif pago.id_metpago == 3:
        if not pago.referencia:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar con cuánto pagará el cliente"
            )
        try:
            cantidad_entregada = Decimal(pago.referencia)
        except Exception:
            raise HTTPException(
                status_code=400, 
                detail="El campo 'referencia' debe ser un número válido"
            )
        if cantidad_entregada < venta_request.total:
            raise HTTPException(
                status_code=400, 
                detail="La cantidad entregada debe ser mayor o igual al total"
            )
        return f"Llevar cambio de '{pago.referencia}'"
    
    else:
        raise HTTPException(
            status_code=400, 
            detail="Método de pago no soportado para domicilio"
        )

def validar_pedido_especial(venta_request):
    """Valida información específica de pedido especial"""
    if venta_request.tipo_servicio == 3:
        if not venta_request.fecha_entrega:
            raise HTTPException(
                status_code=400,
                detail="Debe especificar la fecha_entrega para pedido especial"
            )

def validar_mesa(venta_request):
    """Valida que se especifique mesa para comer aquí"""
    if venta_request.tipo_servicio == 0:
        if venta_request.mesa is None:
            raise HTTPException(
                status_code=400,
                detail="Debe especificar el número de mesa para comer aquí"
            )

def validar_sucursal(venta_request, session: Session):
    """Valida que la sucursal exista"""
    sucursal = session.get(Sucursal, venta_request.id_suc)
    if not sucursal:
        raise HTTPException(
            status_code=404,
            detail=f"Sucursal con ID {venta_request.id_suc} no encontrada"
        )
    return sucursal


def crear_venta_base(venta_request, detalles_domicilio, session: Session):
    """Crea el registro base de la venta"""
    nueva_venta = Venta(
        id_suc=venta_request.id_suc,
        mesa=venta_request.mesa if venta_request.tipo_servicio == 0 else None,
        fecha_hora=datetime.now(),
        total=Decimal(str(venta_request.total)),
        comentarios=venta_request.comentarios,
        tipo_servicio=venta_request.tipo_servicio,
        status=venta_request.status,
        nombreClie=venta_request.nombreClie,
        id_caja=venta_request.id_caja,
        detalles=detalles_domicilio if venta_request.tipo_servicio == 2 else None
    )
    session.add(nueva_venta)
    session.flush()
    return nueva_venta

def crear_registro_domicilio(venta_request, id_venta, session: Session):
    """Crea el registro de domicilio en pDireccion"""
    if venta_request.tipo_servicio != 2:
        return
    
    nuevo_domicilio = pDireccion(
        id_clie=venta_request.id_cliente,
        id_dir=venta_request.id_direccion,
        id_venta=id_venta,
        detalles=None
    )
    session.add(nuevo_domicilio)
    
    # Registrar pago solo si es transferencia
    if venta_request.pagos and venta_request.pagos[0].id_metpago == 1:
        pago = venta_request.pagos[0]
        nuevo_pago = Pago(
            id_venta=id_venta,
            id_metpago=pago.id_metpago,
            monto=Decimal(str(pago.monto)),
            referencia=pago.referencia
        )
        session.add(nuevo_pago)

def crear_pedido_especial(venta_request, id_venta, session: Session):
    """Crea el registro de pedido especial"""
    if venta_request.tipo_servicio != 3:
        return
    
    nuevo_pedido_especial = PEspecial(
        id_venta=id_venta,
        id_dir=venta_request.id_direccion,
        id_clie=venta_request.id_cliente,
        fecha_creacion=datetime.now(),
        fecha_entrega=venta_request.fecha_entrega
    )
    session.add(nuevo_pedido_especial)

def crear_pagos(venta_request, id_venta, session: Session):
    """Crea los registros de pago para tipos de servicio que los requieren"""
    pagos_creados = []
    
    if venta_request.tipo_servicio not in [1, 3] or not venta_request.pagos:
        return pagos_creados
    
    for pago_request in venta_request.pagos:
        nuevo_pago = Pago(
            id_venta=id_venta,
            id_metpago=pago_request.id_metpago,
            monto=Decimal(str(pago_request.monto)),
            referencia=pago_request.referencia
        )
        session.add(nuevo_pago)
        
        pago_info = {
            "id_metpago": pago_request.id_metpago,
            "monto": float(pago_request.monto)
        }
        if pago_request.referencia:
            pago_info["referencia"] = pago_request.referencia
        
        pagos_creados.append(pago_info)
    
    return pagos_creados

def crear_detalles_venta(venta_request, id_venta, session: Session):
    """Crea los detalles de la venta (items)"""
    for item in venta_request.items:
        ingredientes_json = None
        if item.ingredientes:
            ingredientes_json = {
                "tamano": item.ingredientes.tamano,
                "ingredientes": item.ingredientes.ingredientes
            }
        
        # Procesar id_paquete como JSON si existe
        id_paquete_json = None
        if item.id_paquete:
            # El modelo ContenidoPaquete ya validó la estructura
            id_paquete_json = {
                "id_paquete": item.id_paquete.id_paquete,
                "id_pizzas": item.id_paquete.id_pizzas,
                "id_refresco": item.id_paquete.id_refresco
            }
            
            # Solo agregar los campos opcionales si tienen valor
            if item.id_paquete.id_alis is not None:
                id_paquete_json["id_alis"] = item.id_paquete.id_alis
            if item.id_paquete.id_hamb is not None:
                id_paquete_json["id_hamb"] = item.id_paquete.id_hamb
        
        nuevo_detalle = DetalleVenta(
            id_venta=id_venta,
            cantidad=item.cantidad,
            precio_unitario=Decimal(str(item.precio_unitario)),
            id_hamb=item.id_hamb,
            id_cos=item.id_cos,
            id_alis=item.id_alis,
            id_spag=item.id_spag,
            id_papa=item.id_papa,
            id_rec=item.id_rec,
            id_barr=item.id_barr,
            id_maris=item.id_maris,
            id_refresco=item.id_refresco,
            id_paquete=id_paquete_json,  # JSON con toda la info del paquete
            id_magno=item.id_magno,
            id_pizza=item.id_pizza,
            ingredientes=ingredientes_json,
            queso=item.queso,
            status=item.status if hasattr(item, 'status') and item.status is not None else 1
        )
        session.add(nuevo_detalle)

def construir_respuesta(venta_request, nueva_venta, pagos_creados, detalles_domicilio):
    """Construye la respuesta del endpoint según el tipo de servicio"""
    respuesta = {
        "Mensaje": "Venta creada exitosamente",
        "id_venta": nueva_venta.id_venta,
        "total": float(nueva_venta.total),
        "tipo_servicio": nueva_venta.tipo_servicio
    }
    
    # Información específica por tipo de servicio
    if venta_request.tipo_servicio == 0:
        respuesta["mesa"] = nueva_venta.mesa
    
    elif venta_request.tipo_servicio == 1:
        respuesta["pagos_registrados"] = pagos_creados
        respuesta["numero_pagos"] = len(pagos_creados)
    
    elif venta_request.tipo_servicio == 2:
        respuesta["id_cliente"] = venta_request.id_cliente
        respuesta["id_direccion"] = venta_request.id_direccion
        respuesta["detalles_pago"] = detalles_domicilio
    
    elif venta_request.tipo_servicio == 3:
        respuesta["id_cliente"] = venta_request.id_cliente
        respuesta["id_direccion"] = venta_request.id_direccion
        respuesta["pagos_registrados"] = pagos_creados
        respuesta["numero_pagos"] = len(pagos_creados)
    
    # Agregar nombreClie si existe
    if venta_request.nombreClie:
        respuesta["nombreClie"] = venta_request.nombreClie
    
    return respuesta

