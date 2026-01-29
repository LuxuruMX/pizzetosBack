from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, update, delete
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_session
from app.models.detallesModel import DetalleVenta
from app.models.ventaModel import Venta, PVersion
from app.models.pagosModel import Pago
from app.models.pDireccionModel import pDireccion
from app.models.DireccionesModel import Direccion
from app.models.pEspecialModel import PEspecial

from app.schemas.ventaSchema import VentaRequest, VentaResponse, RegistrarPagoRequest, VentaEditRequest

from app.models.clienteModel import Cliente
from app.models.sucursalModel import Sucursal

router = APIRouter()


from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, timedelta


from app.api.refactors.posRefactor import (validar_cliente_direccion,
                                 crear_detalles_venta,
                                 validar_items,
                                 validar_pagos_tipo_servicio,
                                 validar_domicilio,
                                 validar_pedido_especial,
                                 validar_mesa,
                                 validar_sucursal,
                                 crear_venta_base,
                                 crear_registro_domicilio,
                                 crear_pedido_especial,
                                 crear_pagos,
                                 crear_detalles_venta,
                                 construir_respuesta)

from app.api.refactors.getsRefactor import (_get_cliente_nombre,
                                             _get_direccion_detalle,
                                             _get_nombre_sucursal,
                                             _calcular_totales_venta,
                                             _contar_productos_venta,
                                             _filtrar_por_fecha,
                                             _obtener_nombre_cliente_por_tipo_servicio,
                                             _procesar_producto_por_tipo)


@router.get("/ver-pedidos-especiales")
async def ver_pedidos_especiales(
    session: Session = Depends(get_session),
    id_suc: int = 1,
    status: Optional[int] = None,
):
    try:
        from app.models.pEspecialModel import PEspecial
        from app.models.ventaModel import Venta
        
        statement = select(PEspecial).order_by(PEspecial.fecha_creacion.asc())

        # Filtrar por sucursal
        if id_suc != 1:
            statement = statement.join(Venta, PEspecial.id_venta == Venta.id_venta).where(Venta.id_suc == id_suc)

        # Filtrar por status
        if status is None:
            statement = statement.where(PEspecial.status == 1)
        else:
            statement = statement.where(PEspecial.status == status)

        pedidos_especiales = session.exec(statement).all()

        resultados = []
        for pedido in pedidos_especiales:
            nombre_cliente = _get_cliente_nombre(session, pedido.id_clie)
            detalles_direccion = _get_direccion_detalle(session, pedido.id_dir)
            total_venta, anticipo, saldo_pendiente = _calcular_totales_venta(session, pedido.id_venta)
            cantidad_productos = _contar_productos_venta(session, pedido.id_venta)

            resultados.append({
                "id_pespeciales": pedido.id_pespeciales,
                "id_venta": pedido.id_venta,
                "cliente_nombre": nombre_cliente,
                "direccion_detalles": detalles_direccion,
                "fecha_creacion": pedido.fecha_creacion,
                "fecha_entrega": pedido.fecha_entrega,
                "total_venta": total_venta,
                "anticipo": anticipo,
                "saldo_pendiente": saldo_pendiente,
                "cantidad_productos": cantidad_productos
            })

        return resultados

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos especiales: {str(e)}")


@router.get("/pedidos-resumen")
async def listar_pedidos_resumen(
    session: Session = Depends(get_session),
    filtro: str = "hoy",
    status: Optional[int] = None,
    id_suc: Optional[int] = None,
):
    try:
        from app.models.ventaModel import Venta
        from app.models.pagosModel import Pago
        
        statement = select(Venta).order_by(Venta.fecha_hora.desc())

        # Aplicar filtro de fecha
        statement = _filtrar_por_fecha(statement, filtro)

        if status is not None:
            statement = statement.where(Venta.status == status)

        if id_suc:
            statement = statement.where(Venta.id_suc == id_suc)

        ventas = session.exec(statement).all()

        pedidos_resumen = []
        for venta in ventas:
            # Verificar si tiene pagos registrados
            statement_pago = select(Pago).where(Pago.id_venta == venta.id_venta)
            pago_existente = session.exec(statement_pago).first()
            pagado = pago_existente is not None

            # Obtener cliente según el tipo de servicio
            nombre_cliente = _obtener_nombre_cliente_por_tipo_servicio(session, venta)

            nombre_sucursal = _get_nombre_sucursal(session, venta.id_suc)
            total_items = _contar_productos_venta(session, venta.id_venta)

            pedido_dict = {
                "id_venta": venta.id_venta,
                "fecha_hora": venta.fecha_hora,
                "cliente": nombre_cliente,
                "tipo_servicio": venta.tipo_servicio,
                "tipo_servicio_texto": {
                    0: "Comer aquí",
                    1: "Para llevar",
                    2: "Domicilio"
                }.get(venta.tipo_servicio, "Desconocido"),
                "mesa": venta.mesa if venta.tipo_servicio == 0 else None,
                "sucursal": nombre_sucursal,
                "status": venta.status,
                "status_texto": {
                    0: "Esperando",
                    1: "Preparando",
                    2: "Completado",
                    5: "Cancelado"
                }.get(venta.status, "Desconocido"),
                "total": float(venta.total),
                "cantidad_items": total_items,
                "pagado": pagado,
                "detalle": venta.detalles
            }
            pedidos_resumen.append(pedido_dict)

        return {
            "pedidos": pedidos_resumen,
            "total": len(pedidos_resumen),
            "filtro_aplicado": filtro,
            "status_filtrado": status,
            "sucursal_filtrada": id_suc
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")


@router.get("/pedidos-cocina")
async def listar_pedidos_cocina(
    session: Session = Depends(get_session),
    filtro: str = "hoy",
    id_suc: Optional[int] = None,
):
    try:
        from app.models.ventaModel import Venta
        from app.models.detallesModel import DetalleVenta
        
        statement = select(Venta).order_by(Venta.fecha_hora.asc())

        # Filtro por fecha
        statement = _filtrar_por_fecha(statement, filtro)

        # Filtrar por status: solo mostrar Esperando (0) y Preparando (1)
        statement = statement.where(Venta.status.in_([0, 1]))

        # Filtro por sucursal
        if id_suc:
            statement = statement.where(Venta.id_suc == id_suc)

        ventas = session.exec(statement).all()

        pedidos_cocina = []
        for venta in ventas:
            # Obtener cliente según el tipo de servicio
            nombre_cliente = _obtener_nombre_cliente_por_tipo_servicio(session, venta)

            # Obtener sucursal
            nombre_sucursal = _get_nombre_sucursal(session, venta.id_suc)

            # Obtener detalles de productos
            statement_detalles = select(DetalleVenta).where(
                DetalleVenta.id_venta == venta.id_venta,
                DetalleVenta.status.in_([0, 1, 2])
            )
            detalles = session.exec(statement_detalles).all()

            # Procesar productos
            productos = []
            for det in detalles:
                productos.extend(_procesar_producto_por_tipo(session, det))

            total_items = sum(det.cantidad for det in detalles)
            

            pedidos_cocina.append({
                "id_venta": venta.id_venta,
                "fecha_hora": venta.fecha_hora,
                "cliente": nombre_cliente,
                "tipo_servicio": venta.tipo_servicio,
                "tipo_servicio_texto": {
                    0: "Comer aquí",
                    1: "Para llevar",
                    2: "Domicilio",
                    3: "Pedido Especial"
                }.get(venta.tipo_servicio, "Desconocido"),
                "mesa": venta.mesa if venta.tipo_servicio == 0 else None,
                "sucursal": nombre_sucursal,
                "status": venta.status,
                "comentarios": venta.comentarios,
                "status_texto": {
                    0: "Preparando",
                    1: "Entregado",
                    2: "Completado"
                }.get(venta.status, "Desconocido"),
                "cantidad_items": total_items,
                "cantidad_productos_diferentes": len(detalles),
                "productos": productos
            })

        return {
            "pedidos": pedidos_cocina,
            "total": len(pedidos_cocina),
            "filtro_aplicado": filtro,
            "status_filtrado": None,
            "sucursal_filtrada": id_suc
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")



@router.get("/pedidos-cocina/verificacion/{id_suc}")
async def verificacion_actualizar(
    id_suc: int,
    session: Session = Depends(get_session),
):
    stmt = select(PVersion.version).where(PVersion.id_suc == id_suc)
    result = session.exec(stmt).first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No existe versión para la sucursal {id_suc}"
        )

    return {
        "id_suc": id_suc,
        "version": result
    }



@router.get("/edit/{id_venta}/detalle")
async def getDetallesEdit(
    id_venta: int,
    session: Session = Depends(get_session)
):
    try:
        venta = session.get(Venta, id_venta)
        if not venta:
            raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")

        statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles = session.exec(statement_detalles).all()

        productos = []
        for det in detalles:
            # Determinar tipo de producto
            tipo = None
            id_catalogo = None
            detalle_paquete = None
            detalle_rectangular = None
            tamaño = None
            # Paquete
            if det.id_paquete:
                tipo = "id_paquete"
                id_catalogo = det.id_paquete
                detalle_paquete = det.detalle_paquete if hasattr(det, 'detalle_paquete') else None
            # Rectangular
            elif det.id_rec:
                tipo = "id_rec"
                id_catalogo = det.id_rec
                detalle_rectangular = det.detalle_rectangular if hasattr(det, 'detalle_rectangular') else None
            # Barra
            elif det.id_barr:
                tipo = "id_barr"
                id_catalogo = det.id_barr
            # Hamburguesa
            elif det.id_hamb:
                tipo = "id_hamb"
                id_catalogo = det.id_hamb
            # Alitas
            elif det.id_alis:
                tipo = "id_alis"
                id_catalogo = det.id_alis
            # Costillas
            elif det.id_cos:
                tipo = "id_cos"
                id_catalogo = det.id_cos
            # Spaguetty
            elif det.id_spag:
                tipo = "id_spag"
                id_catalogo = det.id_spag
            # Papas
            elif det.id_papa:
                tipo = "id_papa"
                id_catalogo = det.id_papa
            # Magno
            elif det.id_magno:
                tipo = "id_magno"
                id_catalogo = det.id_magno
            # Mariscos
            elif det.id_maris:
                tipo = "id_maris"
                id_catalogo = det.id_maris
            # Refresco
            elif det.id_refresco:
                tipo = "id_refresco"
                id_catalogo = det.id_refresco
            # Pizza
            elif det.id_pizza:
                tipo = "id_pizza"
                id_catalogo = det.id_pizza
            # Custom pizza (ejemplo)
            elif det.ingredientes:
                tipo = "custom_pizza"
                id_catalogo = det.ingredientes
            else:
                tipo = "otro"
                id_catalogo = 0

            prod = {
                "id": id_catalogo if id_catalogo is not None else 0,
                "tipo": tipo,
                "cantidad": det.cantidad,
                "queso": float(det.queso) if det.queso else None,
                "status": det.status
            }
            if tamaño:
                prod["tamaño"] = tamaño
            if detalle_paquete:
                prod["detalle_paquete"] = detalle_paquete
            if detalle_rectangular:
                prod["detalle_rectangular"] = detalle_rectangular
            if hasattr(det, 'precio_unitario') and det.precio_unitario:
                prod["precio"] = float(det.precio_unitario)
            productos.append(prod)

        return {
            "id_venta": venta.id_venta,
            "productos": productos
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalle del pedido: {str(e)}")



@router.get("/pedidos-cocina/{id_venta}/detalle")
async def obtener_detalle_pedido_cocina(
    id_venta: int,
    session: Session = Depends(get_session)
):
    try:
        from app.models.ventaModel import Venta
        from app.models.detallesModel import DetalleVenta
        from app.models.pDireccionModel import pDireccion
        from app.models.pEspecialModel import PEspecial
        
        # Obtener venta
        venta = session.get(Venta, id_venta)
        if not venta:
            raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")

        # Obtener cliente según el tipo de servicio (misma lógica que en el listado)
        nombre_cliente = _obtener_nombre_cliente_por_tipo_servicio(session, venta)

        # Obtener sucursal
        nombre_sucursal = _get_nombre_sucursal(session, venta.id_suc)

        # Obtener detalles de productos
        statement_detalles = select(DetalleVenta).where(
            DetalleVenta.id_venta == id_venta,
            DetalleVenta.status.in_([0, 1, 2])  # Solo los status válidos
        )
        detalles = session.exec(statement_detalles).all()

        # Procesar productos
        productos = []
        for det in detalles:
            productos.extend(_procesar_producto_por_tipo(session, det))

        total_items = sum(det.cantidad for det in detalles)

        # Obtener información específica para domicilio o pedido especial
        id_direccion = None
        fecha_entrega = None
        
        if venta.tipo_servicio == 2:  # Domicilio
            statement_domicilio = select(pDireccion).where(pDireccion.id_venta == venta.id_venta)
            domicilio = session.exec(statement_domicilio).first()
            if domicilio:
                id_direccion = domicilio.id_dir
        
        elif venta.tipo_servicio == 3:  # Pedido Especial
            statement_pespecial = select(PEspecial).where(PEspecial.id_venta == venta.id_venta)
            pedido_especial = session.exec(statement_pespecial).first()
            if pedido_especial:
                id_direccion = pedido_especial.id_dir
                fecha_entrega = pedido_especial.fecha_entrega

        # Obtener información de dirección si existe
        detalle_direccion = None
        if id_direccion:
            detalle_direccion = _get_direccion_detalle(session, id_direccion)

        response = {
            "id_venta": venta.id_venta,
            "fecha_hora": venta.fecha_hora,
            "cliente": nombre_cliente,
            "tipo_servicio": venta.tipo_servicio,
            "tipo_servicio_texto": {
                0: "Comer aquí",
                1: "Para llevar",
                2: "Domicilio",
                3: "Pedido Especial"
            }.get(venta.tipo_servicio, "Desconocido"),
            "mesa": venta.mesa if venta.tipo_servicio == 0 else None,
            "sucursal": nombre_sucursal,
            "status": venta.status,
            "comentarios": venta.comentarios,
            "status_texto": {
                0: "Esperando",
                1: "Preparando",
                2: "Completado"
            }.get(venta.status, "Desconocido"),
            "cantidad_items": total_items,
            "cantidad_productos_diferentes": len(detalles),
            "productos": productos
        }
        
        # Agregar información de dirección y fecha de entrega si es necesario
        if detalle_direccion:
            response["direccion"] = detalle_direccion
        
        if fecha_entrega:
            response["fecha_entrega"] = fecha_entrega
        
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalle del pedido: {str(e)}")


@router.post("/")
async def crear_venta(
    venta_request: VentaRequest,
    session: Session = Depends(get_session)
):
    try:
        # Validaciones
        validar_items(venta_request)
        validar_pagos_tipo_servicio(venta_request)
        validar_cliente_direccion(venta_request, session)
        detalles_domicilio = validar_domicilio(venta_request)
        validar_pedido_especial(venta_request)
        validar_mesa(venta_request)
        validar_sucursal(venta_request, session)
        
        nueva_venta = crear_venta_base(venta_request, detalles_domicilio, session)
        crear_registro_domicilio(venta_request, nueva_venta.id_venta, session)
        crear_pedido_especial(venta_request, nueva_venta.id_venta, session)
        pagos_creados = crear_pagos(venta_request, nueva_venta.id_venta, session)
        crear_detalles_venta(venta_request, nueva_venta.id_venta, session)
        
        # Commit de la transacción
        session.commit()
        
        # Construir y retornar respuesta
        return construir_respuesta(
            venta_request, 
            nueva_venta, 
            pagos_creados, 
            detalles_domicilio
        )
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar la venta: {str(e)}"
        )



@router.post("/pagar")
async def registrar_pago_venta(
    pago_request: RegistrarPagoRequest,
    session: Session = Depends(get_session)
):
    # 1. Verificar que la venta existe
    venta = session.get(Venta, pago_request.id_venta)
    if not venta:
        raise HTTPException(
            status_code=404, 
            detail=f"Venta con ID {pago_request.id_venta} no encontrada"
        )
    
    # 2. Verificar tipo de servicio
    if venta.tipo_servicio not in [0, 2, 3]:
        raise HTTPException(
            status_code=400,
            detail=f"Este endpoint es solo para ventas tipo 0, 2 o 3."
        )
    
    # 3. Calcular acumulado
    statement = select(Pago).where(Pago.id_venta == pago_request.id_venta)
    pagos_existentes = session.exec(statement).all()
    
    monto_pagado_anteriormente = sum(p.monto for p in pagos_existentes)
    suma_nuevos_pagos = sum(pago.monto for pago in pago_request.pagos)
    total_acumulado = monto_pagado_anteriormente + suma_nuevos_pagos
    
    try:
        # 4. Validaciones de monto
        if venta.tipo_servicio in [0, 2]:
            if abs(total_acumulado - venta.total) > Decimal('0.01'):
                remaining = venta.total - monto_pagado_anteriormente
                raise HTTPException(
                    status_code=400,
                    detail=f'El pago debe cubrir el total. Resta: ${remaining}'
                )
                
        elif venta.tipo_servicio == 3:
            if total_acumulado > venta.total + Decimal('0.01'):
                remaining = venta.total - monto_pagado_anteriormente
                raise HTTPException(
                    status_code=400,
                    detail=f'El pago excede el total. Solo resta: ${remaining}'
                )
        
        # 5. Crear registros de pago
        pagos_creados = []
        for pago_data in pago_request.pagos:
            nuevo_pago = Pago(
                id_venta=pago_request.id_venta,
                id_metpago=pago_data.id_metpago,
                monto=Decimal(str(pago_data.monto)),
                referencia=pago_data.referencia
            )
            session.add(nuevo_pago)
            
            pago_info = {
                "id_metpago": pago_data.id_metpago,
                "monto": float(pago_data.monto)
            }
            if pago_data.referencia:
                pago_info["referencia"] = pago_data.referencia
            pagos_creados.append(pago_info)

        if total_acumulado >= venta.total:
            venta.status = 2
            session.add(venta) # Marcamos la venta para actualizar
            
        session.commit()
        session.refresh(venta) # Refrescamos para asegurar que tenemos el status nuevo
        
        # 6. Responder
        saldo_pendiente = float(venta.total - total_acumulado)
        if saldo_pendiente < 0: saldo_pendiente = 0
        
        response = {
            "Mensaje": "Pago registrado exitosamente",
            "id_venta": pago_request.id_venta,
            "tipo_servicio": venta.tipo_servicio,
            "total_venta": float(venta.total),
            "total_pagado": float(total_acumulado),
            "saldo_pendiente": saldo_pendiente,
            "pagos_nuevos": pagos_creados,
            "status_actualizado": venta.status # Aquí verás el 2 si se actualizó
        }
        
        if venta.tipo_servicio == 3 and saldo_pendiente > 0:
            response["nota"] = "Abono registrado. Saldo pendiente."
            
        return response
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



@router.get("/{id_venta}", response_model=VentaResponse)
async def obtener_venta(
    id_venta: int,
    session: Session = Depends(get_session)
):
    # Obtener venta
    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    # Obtener detalles
    statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
    detalles_db = session.exec(statement).all()
    
    # Construir respuesta
    detalles_respuesta = []
    for det in detalles_db:
        subtotal = det.cantidad * det.precio_unitario
        detalles_respuesta.append({
            "cantidad": det.cantidad,
            "precio_unitario": float(det.precio_unitario),
            "subtotal": float(subtotal)
        })
    
    return VentaResponse(
        id_venta=venta.id_venta,
        id_suc=venta.id_suc,
        id_cliente=venta.id_cliente,
        fecha_hora=venta.fecha_hora,
        total=float(venta.total),
        detalles=detalles_respuesta
    )



@router.put("/{id_venta}")
async def editar_venta(
    id_venta: int,
    venta_request: VentaEditRequest,  # Modelo específico
    session: Session = Depends(get_session)
):
    try:
        # Verificar que la venta existe
        venta = session.get(Venta, id_venta)
        if not venta:
            raise HTTPException(
                status_code=404,
                detail=f"Venta con ID {id_venta} no encontrada"
            )

        venta.total = Decimal(str(venta_request.total))
        venta.comentarios = venta_request.comentarios

        # Actualizar la fecha y hora al momento actual
        venta.fecha_hora = datetime.now()

        # Si la venta está completada (status=2), al editarla vuelve a esperando (status=0)
        if venta.status == 2:
            venta.status = 0

        # Opcional: actualizar status si se envió
        if hasattr(venta_request, 'status') and venta_request.status is not None:
            venta.status = venta_request.status

        # Agregar la venta a la sesión para registrar los cambios
        session.add(venta)

        # Eliminar detalles existentes
        stmt = delete(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        session.exec(stmt)

        # Crear los nuevos detalles
        crear_detalles_venta(venta_request, id_venta, session)

        # Commit
        session.commit()
        session.refresh(venta)

        return {
            "Mensaje": "Venta actualizada exitosamente",
            "id_venta": venta.id_venta,
            "total": float(venta.total),
            "comentarios": venta.comentarios,
            "items_actualizados": len(venta_request.items),
            "fecha_hora_actualizada": str(venta.fecha_hora)
        }

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al editar la venta: {str(e)}"
        )



@router.delete("/{id_venta}")
async def eliminar_venta(
    id_venta: int,
    session: Session = Depends(get_session)
):
    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    try:
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles = session.exec(statement).all()
        for detalle in detalles:
            session.delete(detalle)
        
        # Eliminar venta
        session.delete(venta)
        session.commit()
        
        return {"Message":"Venta eliminada exitosamente"}
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar la venta: {str(e)}")



@router.get("/")
async def listar_ventas(
    session: Session = Depends(get_session),
    filtro: str = "hoy",
    status: Optional[int] = None,
    id_suc: Optional[int] = None,
):
    try:
        # Construir query base
        statement = select(Venta).order_by(Venta.fecha_hora.asc())

        if filtro == "hoy":
            hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = hoy_inicio + timedelta(days=1)
            statement = statement.where(
                Venta.fecha_hora >= hoy_inicio,
                Venta.fecha_hora < hoy_fin
            )

        if status is not None:
            statement = statement.where(Venta.status == status)

        if id_suc:
            statement = statement.where(Venta.id_suc == id_suc)

        ventas = session.exec(statement).all()

        ventas_resumidas = []
        for venta in ventas:
            # Obtener cliente
            cliente = session.get(Cliente, venta.id_cliente)
            nombre_cliente = cliente.nombre if cliente else "Desconocido"

            # Obtener sucursal
            sucursal = session.get(Sucursal, venta.id_suc)
            nombre_sucursal = sucursal.nombre if sucursal else "Desconocida"

            # Contar items
            statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == venta.id_venta)
            detalles = session.exec(statement_detalles).all()
            total_items = sum(det.cantidad for det in detalles)

            ventas_resumidas.append({
                "id_venta": venta.id_venta,
                "fecha_hora": venta.fecha_hora,
                "cliente": nombre_cliente,
                "sucursal": nombre_sucursal,
                "status": venta.status,
                "total": float(venta.total),
                "cantidad_items": total_items,
                "cantidad_productos": len(detalles)
            })

        return {
            "ventas": ventas_resumidas,
            "total": len(ventas_resumidas),
            "filtro_aplicado": filtro,
            "status_filtrado": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")



@router.patch("/{id_venta}/toggle-preparacion")
async def toggle_preparacion(
    id_venta: int,
    session: Session = Depends(get_session)
):

    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    try:
        if venta.status == 0:
            venta.status = 1
            mensaje = "Pedido marcado como 'Preparando'"
        elif venta.status == 1:
            venta.status = 0
            mensaje = "Pedido regresado a 'Esperando'"
        else:
            raise HTTPException(
                status_code=400,
                detail="No se puede cambiar el estado. El pedido ya está completado."
            )
        
        session.add(venta)
        session.commit()
        session.refresh(venta)
        
        return {
            "message": mensaje,
            "id_venta": venta.id_venta,
            "nuevo_status": venta.status,
            "status_texto": {0: "Esperando", 1: "Preparando"}[venta.status]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar status: {str(e)}")



@router.patch("/{id_venta}/completar")
async def completar_pedido(
    id_venta: int,
    session: Session = Depends(get_session)
):

    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    try:
        if venta.status != 1:
            raise HTTPException(
                status_code=400,
                detail=f"Solo se pueden completar pedidos en preparación. Estado actual: {venta.status}"
            )
        
        # Cambiar el estado de la venta
        venta.status = 2
        session.add(venta)

        # Cambiar el estado de todos los detalles de venta asociados
        stmt = (
            update(DetalleVenta)
            .where(DetalleVenta.id_venta == id_venta)
            .values(status=2)
        )
        session.exec(stmt)

        session.commit()
        session.refresh(venta)
        
        return {
            "message": "Pedido completado exitosamente",
            "id_venta": venta.id_venta,
            "nuevo_status": 2,
            "status_texto": "Completado"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al completar pedido: {str(e)}")


@router.patch("/completar-pespecial/{id_pespeciales}")
async def completar_pedido_y_pespecial_por_id(
    id_pespeciales: int,
    session: Session = Depends(get_session)
):
    """Completa la venta asociada al `PEspecial` y marca el `PEspecial` con status=2."""
    pedido_especial = session.get(PEspecial, id_pespeciales)
    if not pedido_especial:
        raise HTTPException(status_code=404, detail=f"PEspecial {id_pespeciales} no encontrado")

    id_venta = pedido_especial.id_venta
    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta asociada {id_venta} no encontrada")

    try:
        # Cambiar el estado de la venta
        venta.status = 2
        session.add(venta)

        # Cambiar el estado de todos los detalles de venta asociados
        stmt = (
            update(DetalleVenta)
            .where(DetalleVenta.id_venta == id_venta)
            .values(status=2)
        )
        session.exec(stmt)

        # Marcar el PEspecial como completado (status=2)
        pedido_especial.status = 2
        session.add(pedido_especial)

        session.commit()
        session.refresh(venta)

        return {
            "message": "Pedido completado y PEspecial actualizado exitosamente",
            "id_pespeciales": id_pespeciales,
            "id_venta": venta.id_venta,
            "nuevo_status": 2,
            "status_texto": "Completado"
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al completar pedido y actualizar PEspecial: {str(e)}")



@router.patch("/{id_venta}/cancelar")
async def cancelar_venta(
    id_venta: int,
    motivo_cancelacion: str,
    session: Session = Depends(get_session)
):
    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(
            status_code=404,
            detail=f"Venta {id_venta} no encontrada"
        )

    try:
        # Cambiar status de Venta a 5 (cancelado)
        venta.status = 5
        venta.detalles = motivo_cancelacion
        session.add(venta)

        # Cambiar status de DetalleVenta a 0 (cancelados)
        statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles = session.exec(statement_detalles).all()
        for detalle in detalles:
            detalle.status = 0
            session.add(detalle)

        # Cambiar status de pDireccion a 0 (cancelados)
        statement_pdireccion = select(pDireccion).where(pDireccion.id_venta == id_venta)
        pdireccion = session.exec(statement_pdireccion).all()
        for pd in pdireccion:
            pd.status = 0
            session.add(pd)

        # Cambiar status de PEspecial a 0 (cancelados)
        statement_pespecial = select(PEspecial).where(PEspecial.id_venta == id_venta)
        pespecial = session.exec(statement_pespecial).all()
        for pe in pespecial:
            pe.status = 0
            session.add(pe)

        session.commit()

        return {
            "mensaje": "Venta cancelada exitosamente",
            "id_venta": id_venta,
            "status_venta": venta.status,
            "detalles": venta.detalles,
            "detalles_cancelados": len(detalles),
            "domicilios_cancelados": len(pdireccion),
            "especiales_cancelados": len(pespecial)
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al cancelar la venta: {str(e)}"
        )


@router.get("/recrea-ticket/{id_venta}")
async def recrea_ticket(
    id_venta: int,
    session: Session = Depends(get_session),
):
    try:
        from app.models.ventaModel import Venta
        from app.models.detallesModel import DetalleVenta
        
        # Obtener venta
        venta = session.exec(select(Venta).where(Venta.id_venta == id_venta)).first()
        if not venta:
            raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
        
        # Obtener cliente según el tipo de servicio
        nombre_cliente = _obtener_nombre_cliente_por_tipo_servicio(session, venta)
        nombre_sucursal = _get_nombre_sucursal(session, venta.id_suc)
        
        # Obtener datos del cliente y dirección según tipo de servicio
        id_cliente = None
        telefono_cliente = None
        direccion_info = {}
        
        if venta.tipo_servicio == 2:  # Domicilio
            # Obtener datos de pDireccion
            pdireccion = session.exec(
                select(pDireccion).where(pDireccion.id_venta == id_venta)
            ).first()
            
            if pdireccion:
                id_cliente = pdireccion.id_clie
                # Obtener teléfono del cliente
                cliente = session.get(Cliente, id_cliente)
                telefono_cliente = cliente.telefono if cliente else None
                
                # Obtener datos de Direccion
                direccion = session.get(Direccion, pdireccion.id_dir)
                if direccion:
                    direccion_info = {
                        "id_dir": direccion.id_dir,
                        "calle": direccion.calle,
                        "manzana": direccion.manzana,
                        "lote": direccion.lote,
                        "colonia": direccion.colonia,
                        "referencia": direccion.referencia
                    }
        
        elif venta.tipo_servicio == 3:  # Pedido Especial
            # Obtener datos de PEspecial
            pespecial = session.exec(
                select(PEspecial).where(PEspecial.id_venta == id_venta)
            ).first()
            
            if pespecial:
                id_cliente = pespecial.id_clie
                # Obtener teléfono del cliente
                cliente = session.get(Cliente, id_cliente)
                telefono_cliente = cliente.telefono if cliente else None
                
                # Obtener datos de Direccion
                direccion = session.get(Direccion, pespecial.id_dir)
                if direccion:
                    direccion_info = {
                        "id_dir": direccion.id_dir,
                        "calle": direccion.calle,
                        "manzana": direccion.manzana,
                        "lote": direccion.lote,
                        "colonia": direccion.colonia,
                        "referencia": direccion.referencia,
                        "fecha_entrega": pespecial.fecha_entrega
                    }
        
        # Obtener detalles de productos
        statement_detalles = select(DetalleVenta).where(
            DetalleVenta.id_venta == venta.id_venta,
            DetalleVenta.status.in_([0, 1, 2])
        )
        detalles = session.exec(statement_detalles).all()
        
        # Procesar productos con información extendida
        productos = []
        total_venta = Decimal("0.00")
        
        for det in detalles:
            # Obtener información base del producto
            producto_info = _procesar_producto_por_tipo(session, det)
            
            # Calcular precios desde DetalleVenta
            precio_base = Decimal(str(det.precio_unitario)) if det.precio_unitario else Decimal("0.00")
            precio_extra = Decimal(str(det.queso)) if det.queso else Decimal("0.00")
            precio_total = precio_base + precio_extra
            
            # Enriquecer cada producto con precio_base y precio_extra
            for prod in producto_info:
                prod["precio_base"] = float(precio_base)
                prod["precio_extra"] = float(precio_extra)
                prod["precioUnitario"] = float(precio_total)
                prod["conQueso"] = bool(det.queso)
                
                # Agregar IDs especiales si existen
                if det.id_paquete:
                    prod["id_paquete"] = det.id_paquete
                if det.id_rec:
                    prod["id_rec"] = det.id_rec
                if det.id_barr:
                    prod["id_barr"] = det.id_barr
                
                productos.append(prod)
                total_venta += precio_total * det.cantidad
        
        total_items = sum(det.cantidad for det in detalles)
        
        respuesta = {
            "id_venta": venta.id_venta,
            "fecha_hora": venta.fecha_hora,
            "cliente": nombre_cliente,
            "telefono": telefono_cliente,
            "tipo_servicio": venta.tipo_servicio,
            "tipo_servicio_texto": {
                0: "Comer aquí",
                1: "Para llevar",
                2: "Domicilio",
                3: "Pedido Especial"
            }.get(venta.tipo_servicio, "Desconocido"),
            "mesa": venta.mesa if venta.tipo_servicio == 0 else None,
            "sucursal": nombre_sucursal,
            "status": venta.status,
            "comentarios": venta.comentarios,
            "status_texto": {
                0: "Esperando",
                1: "Preparando",
                2: "Completado"
            }.get(venta.status, "Desconocido"),
            "cantidad_items": total_items,
            "cantidad_productos_diferentes": len(detalles),
            "total_venta": float(total_venta),
            "productos": productos
        }
        
        # Agregar dirección si existe
        if direccion_info:
            respuesta["direccion"] = direccion_info
        
        return respuesta    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al recrear ticket: {str(e)}"
        )