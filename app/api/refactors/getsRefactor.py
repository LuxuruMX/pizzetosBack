from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime, timedelta
import json

from app.models.ventaModel import Venta

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
    """Procesar productos personalizados con ingredientes"""
    from app.models.ventaModel import Ingredientes
    from app.models.tamanosPizzasModel import tamanosPizzas
    
    try:
        ingredientes_data = det.ingredientes
        tamano_id = ingredientes_data.get("tamano")
        ids_ingredientes = ingredientes_data.get("ingredientes", [])
        
        # Obtener el nombre del tamaño
        statement_tamano = select(tamanosPizzas).where(tamanosPizzas.id_tamañop == tamano_id)
        tamano_obj = session.exec(statement_tamano).first()
        nombre_tamano = tamano_obj.tamano if tamano_obj else "Tamaño desconocido"
        
        # Obtener nombres de los ingredientes
        nombres_ingredientes = []
        for id_ing in ids_ingredientes:
            ingrediente = session.get(Ingredientes, id_ing)
            if ingrediente:
                nombres_ingredientes.append(ingrediente.ingrediente)
            else:
                nombres_ingredientes.append(f"Ingrediente #{id_ing}")
        
        return {
            "cantidad": det.cantidad,
            "nombre": f"Pizza Personalizada - {nombre_tamano}",
            "tipo": "Pizza Personalizada",
            "status": det.status,
            "es_personalizado": True,
            "tamano": nombre_tamano,
            "detalles_ingredientes": {
                "tamano": nombre_tamano,
                "tamano_id": tamano_id,
                "ingredientes": nombres_ingredientes,
                "cantidad_ingredientes": len(nombres_ingredientes)
            }
        }
    except Exception as e:
        return {
            "cantidad": det.cantidad,
            "nombre": "Pizza Personalizada - Error al cargar",
            "tipo": "Pizza Personalizada",
            "status": det.status,
            "es_personalizado": True,
            "tamano": "Error",
            "detalles_ingredientes": {"error": str(e)}
        }


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
    from app.models.pizzasModel import pizzas
    from app.models.tamanosPizzasModel import tamanosPizzas
    from app.models.especialidadModel import especialidad
    
    producto = session.get(pizzas, det.id_pizza)
    if not producto:
        return None
    
    try:
        especialidad_obj = session.get(especialidad, producto.id_esp)
        tamano_obj = session.get(tamanosPizzas, producto.id_tamano)
        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else f"Especialidad #{producto.id_esp}"
        tamanoP = tamano_obj.tamano if tamano_obj else f"Tamaño #{producto.id_tamano}"
    except:
        nombre_especialidad = f"Especialidad #{producto.id_esp}"
        tamanoP = f"Tamaño #{producto.id_tamano}"
    
    return {
        "cantidad": det.cantidad,
        "nombre": f"{nombre_especialidad} - {tamanoP}",
        "tipo": "Pizza",
        "status": det.status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": tamanoP
    }


def _procesar_hamburguesa(session: Session, det) -> Optional[Dict[str, Any]]:
    from app.models.hamburguesasModel import hamburguesas
    producto = session.get(hamburguesas, det.id_hamb)
    if not producto:
        return None
    
    return {
        "cantidad": det.cantidad,
        "nombre": producto.paquete,
        "tipo": "Hamburguesa",
        "status": det.status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def _procesar_costilla(session: Session, det) -> Optional[Dict[str, Any]]:
    from app.models.costillasModel import costillas
    producto = session.get(costillas, det.id_cos)
    if not producto:
        return None
    
    return {
        "cantidad": det.cantidad,
        "nombre": producto.orden,
        "tipo": "Costilla",
        "status": det.status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def _procesar_alitas(session: Session, det) -> Optional[Dict[str, Any]]:
    from app.models.alitasModel import alitas
    producto = session.get(alitas, det.id_alis)
    if not producto:
        return None
    
    return {
        "cantidad": det.cantidad,
        "nombre": producto.orden,
        "tipo": "Alitas",
        "status": det.status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def _procesar_spaghetti(session: Session, det) -> Optional[Dict[str, Any]]:
    from app.models.spaguettyModel import spaguetty
    producto = session.get(spaguetty, det.id_spag)
    if not producto:
        return None
    
    return {
        "cantidad": det.cantidad,
        "nombre": producto.orden,
        "tipo": "Spaghetti",
        "status": det.status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def _procesar_papas(session: Session, det) -> Optional[Dict[str, Any]]:
    from app.models.papasModel import papas
    producto = session.get(papas, det.id_papa)
    if not producto:
        return None
    
    return {
        "cantidad": det.cantidad,
        "nombre": producto.orden,
        "tipo": "Papas",
        "status": det.status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def _procesar_mariscos(session: Session, det) -> Optional[Dict[str, Any]]:
    from app.models.mariscosModel import mariscos
    from app.models.tamanosPizzasModel import tamanosPizzas
    
    producto = session.get(mariscos, det.id_maris)
    if not producto:
        return None
    
    try:
        tamano_obj = session.get(tamanosPizzas, producto.id_tamañop) if hasattr(producto, 'id_tamañop') else None
        tamano_marisco = tamano_obj.tamano if tamano_obj else "Tamaño desconocido"
        nombre_producto = f"{producto.nombre} - {tamano_marisco}"
        tamano = tamano_marisco
    except:
        nombre_producto = producto.nombre
        tamano = "Tamaño desconocido"
    
    return {
        "cantidad": det.cantidad,
        "nombre": nombre_producto,
        "tipo": "Mariscos",
        "status": det.status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": tamano
    }


def _procesar_refresco(session: Session, det) -> Optional[Dict[str, Any]]:
    from app.models.refrescosModel import refrescos
    producto = session.get(refrescos, det.id_refresco)
    if not producto:
        return None
    
    return {
        "cantidad": det.cantidad,
        "nombre": producto.nombre,
        "tipo": "Refresco",
        "status": det.status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def _procesar_magno(session: Session, det) -> List[Dict[str, Any]]:
    from app.models.magnoModel import magno
    from app.models.especialidadModel import especialidad
    
    try:
        lista_ids = json.loads(det.id_magno) if isinstance(det.id_magno, str) else det.id_magno
    except:
        lista_ids = det.id_magno if isinstance(det.id_magno, list) else [det.id_magno]
    
    nombres_magno = []
    for id_mag in lista_ids:
        producto = session.get(magno, id_mag)
        if producto:
            try:
                especialidad_obj = session.get(especialidad, producto.id_especialidad)
                nombre_especialidad = especialidad_obj.nombre if especialidad_obj else f"Especialidad #{producto.id_especialidad}"
            except:
                nombre_especialidad = f"Especialidad #{producto.id_especialidad}"
            nombres_magno.append(nombre_especialidad)
    
    if nombres_magno:
        return [{
            "cantidad": det.cantidad,
            "nombre": "Magno",
            "tipo": "Magno",
            "especialidades": nombres_magno,
            "status": det.status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    return []


def _procesar_rectangular(session: Session, det) -> List[Dict[str, Any]]:
    from app.models.rectangularModel import rectangular
    from app.models.especialidadModel import especialidad
    
    try:
        lista_ids = json.loads(det.id_rec) if isinstance(det.id_rec, str) else det.id_rec
    except:
        lista_ids = det.id_rec if isinstance(det.id_rec, list) else [det.id_rec]
    
    nombres_rect = []
    for id_rec in lista_ids:
        producto = session.get(rectangular, id_rec)
        if producto:
            try:
                especialidad_obj = session.get(especialidad, producto.id_esp)
                nombre_especialidad = especialidad_obj.nombre if especialidad_obj else f"Especialidad #{producto.id_esp}"
            except:
                nombre_especialidad = f"Especialidad #{producto.id_esp}"
            nombres_rect.append(nombre_especialidad)
    
    if nombres_rect:
        return [{
            "cantidad": det.cantidad,
            "nombre": "Rectangular",
            "tipo": "Rectangular",
            "especialidades": nombres_rect,
            "status": det.status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    return []


def _procesar_barra(session: Session, det) -> List[Dict[str, Any]]:
    from app.models.barraModel import barra
    from app.models.especialidadModel import especialidad
    
    try:
        lista_ids = json.loads(det.id_barr) if isinstance(det.id_barr, str) else det.id_barr
    except:
        lista_ids = det.id_barr if isinstance(det.id_barr, list) else [det.id_barr]
    
    nombres_barr = []
    for id_barr in lista_ids:
        producto = session.get(barra, id_barr)
        if producto:
            try:
                especialidad_obj = session.get(especialidad, producto.id_especialidad)
                nombre_especialidad = especialidad_obj.nombre if especialidad_obj else f"Especialidad #{producto.id_especialidad}"
            except:
                nombre_especialidad = f"Especialidad #{producto.id_especialidad}"
            nombres_barr.append(nombre_especialidad)
    
    if nombres_barr:
        return [{
            "cantidad": det.cantidad,
            "nombre": "Barra",
            "tipo": "Barra",
            "especialidades": nombres_barr,
            "status": det.status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    return []


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
    from app.models.pizzasModel import pizzas
    from app.models.especialidadModel import especialidad
    
    productos = []
    if det.detalle_paquete:
        ids_pizzas = det.detalle_paquete.split(",")
        
        for id_pizza_str in ids_pizzas:
            try:
                id_pizza = int(id_pizza_str.strip())
                pizza = session.get(pizzas, id_pizza)
                
                if pizza:
                    try:
                        especialidad_obj = session.get(especialidad, pizza.id_esp)
                        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else f"Especialidad #{pizza.id_esp}"
                    except:
                        nombre_especialidad = f"Especialidad #{pizza.id_esp}"
                    
                    pizza_info = {
                        "cantidad": 1,
                        "nombre": nombre_especialidad,
                        "tipo": f"Paquete {det.id_paquete} - Pizza",
                        "status": det.status,
                        "es_personalizado": False,
                        "detalles_ingredientes": None,
                        "tamano": None
                    }
                    productos.append(pizza_info)
            
            except (ValueError, AttributeError) as e:
                error_info = {
                    "cantidad": 1,
                    "nombre": f"Error al cargar pizza del paquete",
                    "tipo": f"Paquete {det.id_paquete}",
                    "status": det.status,
                    "es_personalizado": False,
                    "detalles_ingredientes": None,
                    "tamano": None
                }
                productos.append(error_info)
    else:
        productos.append({
            "cantidad": det.cantidad,
            "nombre": f"Paquete {det.id_paquete} - Sin detalle",
            "tipo": "Paquete",
            "status": det.status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        })
    
    return productos


def _procesar_paquetes_tipo_2(session: Session, det) -> List[Dict[str, Any]]:
    from app.models.pizzasModel import pizzas
    from app.models.especialidadModel import especialidad
    from app.models.alitasModel import alitas
    from app.models.refrescosModel import refrescos
    from app.models.hamburguesasModel import hamburguesas
    from app.models.tamanosPizzasModel import tamanosPizzas
    
    productos = []
    
    # Refresco
    if det.id_refresco:
        refresco = session.get(refrescos, det.id_refresco)
        if refresco:
            refresco_info = {
                "cantidad": 1,
                "nombre": refresco.nombre,
                "tipo": f"Paquete {det.id_paquete} - Refresco",
                "status": det.status,
                "es_personalizado": False,
                "detalles_ingredientes": None,
                "tamano": None
            }
            productos.append(refresco_info)
    
    # Pizza
    if det.id_pizza:
        producto = session.get(pizzas, det.id_pizza)
        if producto:
            try:
                especialidad_obj = session.get(especialidad, producto.id_esp)
                nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
            except:
                nombre_especialidad = f"Especialidad #{producto.id_esp}"
            
            try:
                tamano_obj = session.get(tamanosPizzas, producto.id_tamano)
                tamanoP = tamano_obj.tamano if tamano_obj else f"Tamaño #{producto.id_tamano}"
            except:
                tamanoP = f"Tamaño #{producto.id_tamano}"
            
            pizza_info = {
                "cantidad": 1,
                "nombre": f"{nombre_especialidad} - {tamanoP}",
                "tipo": f"Paquete {det.id_paquete} - Pizza",
                "status": det.status,
                "es_personalizado": False,
                "detalles_ingredientes": None,
                "tamano": tamanoP
            }
            productos.append(pizza_info)
    
    # Alitas o Hamburguesa
    if det.id_alis:
        alita = session.get(alitas, det.id_alis)
        if alita:
            alita_info = {
                "cantidad": 1,
                "nombre": alita.orden,
                "tipo": f"Paquete {det.id_paquete} - Alitas",
                "status": det.status,
                "es_personalizado": False,
                "detalles_ingredientes": None,
                "tamano": None
            }
            productos.append(alita_info)
    elif det.id_hamb:
        hamburguesa = session.get(hamburguesas, det.id_hamb)
        if hamburguesa:
            hamb_info = {
                "cantidad": 1,
                "nombre": hamburguesa.paquete,
                "tipo": f"Paquete {det.id_paquete} - Hamburguesa",
                "status": det.status,
                "es_personalizado": False,
                "detalles_ingredientes": None,
                "tamano": None
            }
            productos.append(hamb_info)
    
    return productos

