from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
import json

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
    
    # Procesar paquete si existe
    if det.id_paquete:
        productos.extend(_procesar_paquete(session, det))
        return productos  # Un detalle es O paquete O producto individual
    
    # Procesar diferentes tipos de productos individuales
    if det.id_pizza:
        producto_info = _procesar_pizza(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_hamb:
        producto_info = _procesar_hamburguesa(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_cos:
        producto_info = _procesar_costilla(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_alis:
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
    
    if det.id_refresco:
        producto_info = _procesar_refresco(session, det)
        if producto_info:
            productos.append(producto_info)
    
    if det.id_magno:
        productos.extend(_procesar_magno(session, det))
    
    if det.id_rec:
        productos.extend(_procesar_rectangular(session, det))
    
    if det.id_barr:
        productos.extend(_procesar_barra(session, det))
    
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
    """Procesar un paquete de productos desde JSON.
    
    El paquete viene como JSON en det.id_paquete con estructura:
    {"id_paquete": 1, "id_pizzas": [4, 8], "id_refresco": 17, "id_hamb": 1, ...}
    """
    if not det.id_paquete:
        return []
    
    # Parsear el JSON si es string, si no es dict ya
    try:
        if isinstance(det.id_paquete, str):
            paquete_data = json.loads(det.id_paquete)
        else:
            paquete_data = det.id_paquete
    except (json.JSONDecodeError, TypeError):
        return []
    
    productos = []
    
    # Procesar Pizzas
    id_pizzas = paquete_data.get('id_pizzas', [])
    if id_pizzas:
        # id_pizzas puede ser lista o string
        if isinstance(id_pizzas, str):
            try:
                id_pizzas = json.loads(id_pizzas)
            except:
                id_pizzas = [id_pizzas]
        
        for pid in id_pizzas:
            pizza_info = procesar_pizza_cached(session, det.cantidad, pid, det.status)
            if pizza_info:
                productos.append(pizza_info)
    
    # Procesar Refresco
    id_refresco = paquete_data.get('id_refresco')
    if id_refresco:
        refresco_info = procesar_refresco_cached(session, det.cantidad, id_refresco, det.status)
        if refresco_info:
            productos.append(refresco_info)
    
    # Procesar Hamburguesa
    id_hamb = paquete_data.get('id_hamb')
    if id_hamb:
        hamb_info = procesar_hamburguesa_cached(session, det.cantidad, id_hamb, det.status)
        if hamb_info:
            productos.append(hamb_info)
    
    # Procesar Alitas
    id_alis = paquete_data.get('id_alis')
    if id_alis:
        alita_info = procesar_alitas_cached(session, det.cantidad, id_alis, det.status)
        if alita_info:
            productos.append(alita_info)
    
    # Procesar Costillas
    id_cos = paquete_data.get('id_cos')
    if id_cos:
        costilla_info = procesar_costilla_cached(session, det.cantidad, id_cos, det.status)
        if costilla_info:
            productos.append(costilla_info)
    
    # Procesar Spaghetti
    id_spag = paquete_data.get('id_spag')
    if id_spag:
        spag_info = procesar_spaghetti_cached(session, det.cantidad, id_spag, det.status)
        if spag_info:
            productos.append(spag_info)
    
    # Procesar Papas
    id_papa = paquete_data.get('id_papa')
    if id_papa:
        papa_info = procesar_papas_cached(session, det.cantidad, id_papa, det.status)
        if papa_info:
            productos.append(papa_info)
    
    # Procesar Mariscos
    id_maris = paquete_data.get('id_maris')
    if id_maris:
        maris_info = procesar_mariscos_cached(session, det.cantidad, id_maris, det.status)
        if maris_info:
            productos.append(maris_info)
    
    return productos

