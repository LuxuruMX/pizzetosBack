from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta

from app.models.ventaModel import Venta
from app.api.refactors.cachedDef import (
    procesar_producto_personalizado_cached,
    procesar_pizza_cached,
    procesar_hamburguesa_cached,
    procesar_costilla_cached,
    procesar_alitas_cached,
    procesar_spaghetti_cached,
    procesar_papas_cached,
    procesar_mariscos_cached,
    procesar_refresco_cached,
    procesar_magno_cached,
    procesar_rectangular_cached,
    procesar_barra_cached,
    procesar_paquetes_tipo_1_3_cached,
    procesar_paquetes_tipo_2_cached
)

# Funciones auxiliares comunes
def _get_cliente_nombre(session: Session, id_cliente: int) -> str:
    """Obtener nombre completo del cliente"""
    from app.models.clienteModel import Cliente
    cliente = session.get(Cliente, id_cliente)
    return f"{cliente.nombre} {cliente.apellido}" if cliente else "Desconocido"


def _get_direccion_detalle(session: Session, id_direccion: int) -> str:
    """Obtener detalle de la dirección"""
    from app.models.DireccionesModel import Direccion
    direccion = session.get(Direccion, id_direccion)
    if direccion:
        return f"{direccion.calle} {direccion.manzana}, {direccion.lote}, {direccion.colonia}, {direccion.referencia}"
    return "Desconocida"


def _get_nombre_sucursal(session: Session, id_sucursal: int) -> str:
    """Obtener nombre de la sucursal"""
    from app.models.sucursalModel import Sucursal
    sucursal = session.get(Sucursal, id_sucursal)
    return sucursal.nombre if sucursal else "Desconocida"


def _calcular_totales_venta(session: Session, id_venta: int) -> tuple[float, float, float]:
    """Calcular total venta, anticipo y saldo pendiente"""
    from app.models.ventaModel import Venta
    from app.models.pagosModel import Pago
    from app.models.detallesModel import DetalleVenta
    
    # Total de la venta
    venta = session.get(Venta, id_venta)
    total_venta = float(venta.total) if venta else 0.0
    
    # Anticipo (suma de pagos)
    statement_pagos = select(Pago).where(Pago.id_venta == id_venta)
    pagos = session.exec(statement_pagos).all()
    anticipo = sum(float(pago.monto) for pago in pagos)
    
    # Saldo pendiente
    saldo_pendiente = total_venta - anticipo
    
    return total_venta, anticipo, saldo_pendiente


def _contar_productos_venta(session: Session, id_venta: int) -> int:
    """Contar cantidad total de productos en una venta"""
    from app.models.detallesModel import DetalleVenta
    statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
    detalles = session.exec(statement_detalles).all()
    return sum(detalle.cantidad for detalle in detalles)


def _filtrar_por_fecha(statement, filtro: str) -> Any:
    """Aplicar filtro de fecha común a diferentes endpoints"""
    now = datetime.now()
    
    if filtro == "hoy":
        hoy_inicio = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = hoy_inicio + timedelta(days=1)
        statement = statement.where(
            Venta.fecha_hora >= hoy_inicio,
            Venta.fecha_hora < hoy_fin
        )
    elif filtro == "semana":
        inicio_semana = now - timedelta(days=now.weekday())
        inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        statement = statement.where(Venta.fecha_hora >= inicio_semana)
    elif filtro == "mes":
        inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        statement = statement.where(Venta.fecha_hora >= inicio_mes)
    # "todos" no necesita filtro adicional
    
    return statement


def _obtener_nombre_cliente_por_tipo_servicio(session: Session, venta) -> str:
    """Obtener nombre del cliente basado en el tipo de servicio"""
    from app.models.pDireccionModel import pDireccion
    from app.models.clienteModel import Cliente
    from app.models.pEspecialModel import PEspecial
    
    if venta.tipo_servicio == 0:  # Comer aquí
        mesa_num = venta.mesa if venta.mesa else "S/N"
        nombre_base = venta.nombreClie if venta.nombreClie else "Sin nombre"
        return f"Mesa {mesa_num} - {nombre_base}"
    
    elif venta.tipo_servicio == 1:  # Para llevar
        return venta.nombreClie if venta.nombreClie else "Para llevar"
    
    elif venta.tipo_servicio == 2:  # Domicilio
        statement_domicilio = select(pDireccion).where(pDireccion.id_venta == venta.id_venta)
        domicilio = session.exec(statement_domicilio).first()
        if domicilio and domicilio.id_clie:
            cliente = session.get(Cliente, domicilio.id_clie)
            return cliente.nombre if cliente else "Cliente sin nombre"
        return venta.nombreClie if venta.nombreClie else "Domicilio sin cliente"
    
    elif venta.tipo_servicio == 3:  # Pedido Especial
        statement_pespecial = select(PEspecial).where(PEspecial.id_venta == venta.id_venta)
        pes = session.exec(statement_pespecial).first()
        if not pes:
            return "Sin información - Especial"
        if not pes.fecha_entrega or pes.fecha_entrega.date() != datetime.now().date():
            return "Sin información - Especial"
        
        cliente = session.get(Cliente, pes.id_clie) if pes.id_clie else None
        return f"{cliente.nombre} {cliente.apellido} - Especial" if cliente else "Sin nombre - Especial"
    
    return "Sin información"


def _procesar_producto_personalizado(session: Session, det) -> Dict[str, Any]:
    """Procesar productos personalizados con ingredientes (versión cacheada)"""
    return procesar_producto_personalizado_cached(
        session, det.cantidad, det.ingredientes, det.status
    )


def _procesar_producto_por_tipo(session: Session, det) -> List[Dict[str, Any]]:
    """Procesar diferentes tipos de productos en un detalle de venta"""
    productos = []
    
    # Pizza personalizada
    if det.ingredientes:
        producto_info = _procesar_producto_personalizado(session, det)
        productos.append(producto_info)
        return productos  # No procesar otros tipos si es personalizado
    
    # Procesar diferentes tipos de productos
    if det.id_pizza and det.id_paquete != 2:
        producto_info = _procesar_pizza(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_hamb and det.id_paquete != 2:
        producto_info = _procesar_hamburguesa(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_cos:
        producto_info = _procesar_costilla(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_alis and det.id_paquete != 2:
        producto_info = _procesar_alitas(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_spag:
        producto_info = _procesar_spaghetti(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_papa:
        producto_info = _procesar_papas(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_maris:
        producto_info = _procesar_mariscos(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_refresco and det.id_paquete != 2:
        producto_info = _procesar_refresco(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_magno:
        productos.extend(_procesar_magno(session, det))
    
    if det.id_rec:
        productos.extend(_procesar_rectangular(session, det))
    
    if det.id_barr:
        productos.extend(_procesar_barra(session, det))
    
    if det.id_paquete:
        productos.extend(_procesar_paquete(session, det))
    
    return productos


def _procesar_pizza(session: Session, det) -> Optional[Dict[str, Any]]:
    return procesar_pizza_cached(session, det.cantidad, det.id_pizza, det.status)


def _procesar_hamburguesa(session: Session, det) -> Optional[Dict[str, Any]]:
    return procesar_hamburguesa_cached(session, det.cantidad, det.id_hamb, det.status)


def _procesar_costilla(session: Session, det) -> Optional[Dict[str, Any]]:
    return procesar_costilla_cached(session, det.cantidad, det.id_cos, det.status)


def _procesar_alitas(session: Session, det) -> Optional[Dict[str, Any]]:
    return procesar_alitas_cached(session, det.cantidad, det.id_alis, det.status)


def _procesar_spaghetti(session: Session, det) -> Optional[Dict[str, Any]]:
    return procesar_spaghetti_cached(session, det.cantidad, det.id_spag, det.status)


def _procesar_papas(session: Session, det) -> Optional[Dict[str, Any]]:
    return procesar_papas_cached(session, det.cantidad, det.id_papa, det.status)


def _procesar_mariscos(session: Session, det) -> Optional[Dict[str, Any]]:
    return procesar_mariscos_cached(session, det.cantidad, det.id_maris, det.status)


def _procesar_refresco(session: Session, det) -> Optional[Dict[str, Any]]:
    return procesar_refresco_cached(session, det.cantidad, det.id_refresco, det.status)


def _procesar_magno(session: Session, det) -> List[Dict[str, Any]]:
    return procesar_magno_cached(session, det.cantidad, det.id_magno, det.status)


def _procesar_rectangular(session: Session, det) -> List[Dict[str, Any]]:
    return procesar_rectangular_cached(session, det.cantidad, det.id_rec, det.status)


def _procesar_barra(session: Session, det) -> List[Dict[str, Any]]:
    return procesar_barra_cached(session, det.cantidad, det.id_barr, det.status)


def _procesar_paquete(session: Session, det) -> List[Dict[str, Any]]:
    if det.id_paquete in [1, 3]:
        return _procesar_paquetes_tipo_1_3(session, det)
    elif det.id_paquete == 2:
        return _procesar_paquetes_tipo_2(session, det)
    else:
        # Otros tipos de paquetes
        return [{
            "cantidad": det.cantidad,
            "nombre": f"Paquete {det.id_paquete} - Sin detalle",
            "tipo": "Paquete",
            "status": det.status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]


def _procesar_paquetes_tipo_1_3(session: Session, det) -> List[Dict[str, Any]]:
    return procesar_paquetes_tipo_1_3_cached(
        session, det.cantidad, det.id_paquete, det.detalle_paquete, det.status
    )


def _procesar_paquetes_tipo_2(session: Session, det) -> List[Dict[str, Any]]:
    return procesar_paquetes_tipo_2_cached(
        session, det.cantidad, det.id_paquete,
        det.id_refresco, det.id_pizza, det.id_alis, det.id_hamb,
        det.status
    )

