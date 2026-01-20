from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, update
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

from app.schemas.ventaSchema import VentaRequest, VentaResponse, RegistrarPagoRequest

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
                    0: "Esperando",
                    1: "Preparando",
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
        # Obtener venta
        venta = session.get(Venta, id_venta)
        if not venta:
            raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")

        # Obtener sucursal
        sucursal = session.get(Sucursal, venta.id_suc)
        nombre_sucursal = sucursal.nombre if sucursal else "Desconocida"

        # Obtener detalles de productos
        statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles = session.exec(statement_detalles).all()

        # Construir lista de productos con nombres
        productos = []
        for det in detalles:
            producto_info = {
                "cantidad": det.cantidad,
                "id": None,
                "tipo": None,
                "tamaño": None,
                "status": det.status
            }

            if det.id_pizza and not det.id_paquete:
                from app.models.pizzasModel import pizzas
                from app.models.tamanosPizzasModel import tamanosPizzas
                
                producto = session.get(pizzas, det.id_pizza)
                if producto:
                    tamano_obj = session.get(tamanosPizzas, producto.id_tamano)
                    nombre_tamano = tamano_obj.tamano if tamano_obj else "Tamaño desconocido"

                    producto_info["id"] = producto.id_pizza
                    producto_info["tamaño"] = nombre_tamano
                    producto_info["tipo"] = "id_pizza"
                productos.append(producto_info)
                
            elif det.id_hamb and not det.id_paquete:
                producto_info["id"] = det.id_hamb
                producto_info["tipo"] = "id_hamb"
                productos.append(producto_info)
            
            elif det.id_cos and not det.id_paquete:
                producto_info["id"] = det.id_cos
                producto_info["tipo"] = "id_cos"
                productos.append(producto_info)
            
            elif det.id_alis and not det.id_paquete:
                producto_info["id"] = det.id_alis
                producto_info["tipo"] = "id_alis"
                productos.append(producto_info)
            
            elif det.id_spag and not det.id_paquete:
                producto_info["id"] = det.id_spag
                producto_info["tipo"] = "id_spag"
                productos.append(producto_info)
            
            elif det.id_papa and not det.id_paquete:
                producto_info["id"] = det.id_papa
                producto_info["tipo"] = "id_papa"
                productos.append(producto_info)
            
            elif det.id_maris and not det.id_paquete:
                producto_info["id"] = det.id_maris
                producto_info["tipo"] = "id_maris"
                productos.append(producto_info)
            
            elif det.id_refresco and not det.id_paquete:
                from app.models.refrescosModel import refrescos
                from app.models.tamanosRefrescosModel import tamanosRefrescos
                producto = session.get(refrescos, det.id_refresco)
                tamano = session.get(tamanosRefrescos, producto.id_tamano)
                if producto:
                    producto_info["id"] = producto.id_refresco
                    producto_info["tipo"] = "id_refresco"
                    producto_info["tamaño"] = tamano.tamano
                productos.append(producto_info)
            
            elif det.id_magno and not det.id_paquete:
                producto_info["id"] = det.id_magno
                producto_info["tipo"] = "id_magno"
                productos.append(producto_info)
            
            elif det.id_rec and not det.id_paquete:
                producto_info["id"] = det.id_rec
                producto_info["tipo"] = "id_rec"
                productos.append(producto_info)
            
            elif det.id_paquete:
                producto_info["id"] = det.id_paquete
                producto_info["tipo"] = "id_paquete"
                productos.append(producto_info)

        # Construir respuesta base
        response = {
            "id_venta": venta.id_venta,
            "fecha_hora": venta.fecha_hora,
            "id_suc": venta.id_suc,
            "sucursal": nombre_sucursal,
            "tipo_servicio": venta.tipo_servicio,
            "status": venta.status,
            "comentarios": venta.comentarios,
            "status_texto": {
                0: "Esperando",
                1: "Preparando",
                2: "Completado"
            }.get(venta.status, "Desconocido"),
            "productos": productos
        }

        # Añadir campos según tipo_servicio
        if venta.tipo_servicio == 0:  # Comedor
            response["mesa"] = venta.mesa
            response["nombreClie"] = venta.nombreClie
        
        elif venta.tipo_servicio == 1:  # Para Llevar
            response["nombreClie"] = venta.nombreClie
            
            # Obtener pagos
            from app.models.pagosModel import Pago
            statement_pagos = select(Pago).where(Pago.id_venta == id_venta)
            pagos = session.exec(statement_pagos).all()
            
            response["pagos"] = [
                {
                    "id_metpago": pago.id_metpago,
                    "monto": pago.monto
                }
                for pago in pagos
            ]
        
        elif venta.tipo_servicio == 2:
            response["id_cliente"] = getattr(venta, 'id_cliente', None)
            response["id_direccion"] = getattr(venta, 'id_direccion', None)

        return response

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
    
    # 2. Verificar tipo de servicio (Comer aquí=0, Domicilio=2, Especial=3)
    if venta.tipo_servicio not in [0, 2, 3]:
        raise HTTPException(
            status_code=400,
            detail=f"Este endpoint es solo para ventas tipo 0, 2 o 3. Esta venta es tipo {venta.tipo_servicio}"
        )
    
    # 3. Obtener pagos previos para calcular acumulado
    statement = select(Pago).where(Pago.id_venta == pago_request.id_venta)
    pagos_existentes = session.exec(statement).all()
    
    monto_pagado_anteriormente = sum(p.monto for p in pagos_existentes)
    suma_nuevos_pagos = sum(pago.monto for pago in pago_request.pagos)
    total_acumulado = monto_pagado_anteriormente + suma_nuevos_pagos
    
    try:
        # 4. Validaciones de monto
        if venta.tipo_servicio in [0, 2]:
            # Para servicio normal, el total acumulado debe cubrir la venta exacta
            # (o la suma nueva si no había pagos previos, logicamente igual)
            if abs(total_acumulado - venta.total) > Decimal('0.01'):
                remaining = venta.total - monto_pagado_anteriormente
                raise HTTPException(
                    status_code=400,
                    detail=f'El pago debe cubrir el total. Resta por pagar: ${remaining}'
                )
                
        elif venta.tipo_servicio == 3:
            # Para pedidos especiales, validar no exceder el total
            if total_acumulado > venta.total + Decimal('0.01'):
                remaining = venta.total - monto_pagado_anteriormente
                raise HTTPException(
                    status_code=400,
                    detail=f'El pago excede el total. Solo resta: ${remaining}'
                )
        
        # 5. Crear los NUEVOS registros de pago
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
        
        session.commit()
        
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
            "status_actualizado": venta.status
        }
        
        if venta.tipo_servicio == 3 and saldo_pendiente > 0:
            response["nota"] = "Abono registrado. Saldo pendiente."
            
        return response
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar pago: {str(e)}")



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
async def actualizar_venta(
    id_venta: int,
    venta_request: VentaRequest,
    session: Session = Depends(get_session)
):
    if not venta_request.items:
        raise HTTPException(status_code=400, detail="La venta debe contener al menos un item")

    # Verificar que la venta existe
    venta_existente = session.get(Venta, id_venta)
    if not venta_existente:
        raise HTTPException(status_code=404, detail=f"Venta con ID {id_venta} no encontrada")

    # Validar pagos si tipo_servicio es 1
    if venta_request.tipo_servicio == 1:
        if not venta_request.pagos or len(venta_request.pagos) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar al menos un método de pago cuando el tipo de servicio es 1 (para llevar)"
            )

    # Validar cliente solo si tipo_servicio es 2 (domicilio)
    if venta_request.tipo_servicio == 2:
        if not venta_request.id_cliente:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el id_cliente cuando el tipo de servicio es 2 (domicilio)"
            )
        
        cliente = session.get(Cliente, venta_request.id_cliente)
        if not cliente:
            raise HTTPException(
                status_code=404, 
                detail=f"Cliente con ID {venta_request.id_cliente} no encontrado"
            )
        
        # Validar que la dirección existe
        if not venta_request.id_direccion:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el id_direccion cuando el tipo de servicio es 2 (domicilio)"
            )
        
        direccion = session.get(Direccion, venta_request.id_direccion)
        if not direccion:
            raise HTTPException(
                status_code=404, 
                detail=f"Dirección con ID {venta_request.id_direccion} no encontrada"
            )

    # Validar mesa si tipo_servicio es 0 (comer aquí)
    if venta_request.tipo_servicio == 0:
        if venta_request.mesa is None:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el número de mesa cuando el tipo de servicio es 0 (comer aquí)"
            )

    # Verificar sucursal
    sucursal = session.get(Sucursal, venta_request.id_suc)
    if not sucursal:
        raise HTTPException(
            status_code=404, 
            detail=f"Sucursal con ID {venta_request.id_suc} no encontrada"
        )

    try:
        # Actualizar datos de la venta
        venta_existente.id_suc = venta_request.id_suc
        venta_existente.mesa = venta_request.mesa if venta_request.tipo_servicio == 0 else None
        venta_existente.total = Decimal(str(venta_request.total))
        venta_existente.comentarios = venta_request.comentarios
        venta_existente.tipo_servicio = venta_request.tipo_servicio
        venta_existente.status = venta_request.status
        venta_existente.nombreClie = venta_request.nombreClie
        
        # Actualizar o crear registro en pDireccion si es domicilio (tipo_servicio = 2)
        if venta_request.tipo_servicio == 2:
            # Buscar si ya existe un registro de domicilio para esta venta
            statement_domicilio = select(pDireccion).where(pDireccion.id_venta == id_venta)
            domicilio_existente = session.exec(statement_domicilio).first()
            
            if domicilio_existente:
                # Actualizar el registro existente
                domicilio_existente.id_clie = venta_request.id_cliente
                domicilio_existente.id_dir = venta_request.id_direccion
            else:
                # Crear nuevo registro
                nuevo_domicilio = pDireccion(
                    id_clie=venta_request.id_cliente,
                    id_dir=venta_request.id_direccion,
                    id_venta=id_venta
                )
                session.add(nuevo_domicilio)
        else:
            # Si cambió el tipo de servicio y ya no es domicilio, eliminar registro de pDireccion si existe
            statement_domicilio = select(pDireccion).where(pDireccion.id_venta == id_venta)
            domicilio_existente = session.exec(statement_domicilio).first()
            if domicilio_existente:
                session.delete(domicilio_existente)
        
        # Manejar pagos si tipo_servicio es 1 (para llevar)
        # Primero eliminar pagos existentes
        statement_pagos = select(Pago).where(Pago.id_venta == id_venta)
        pagos_existentes = session.exec(statement_pagos).all()
        for pago in pagos_existentes:
            session.delete(pago)
        
        # Crear nuevos pagos si tipo_servicio es 1
        pagos_creados = []
        if venta_request.tipo_servicio == 1 and venta_request.pagos:
            for pago_request in venta_request.pagos:
                nuevo_pago = Pago(
                    id_venta=id_venta,
                    id_metpago=pago_request.id_metpago,
                    monto=Decimal(str(pago_request.monto))
                )
                session.add(nuevo_pago)
                pagos_creados.append({
                    "id_metpago": pago_request.id_metpago,
                    "monto": float(pago_request.monto)
                })
        
        session.flush()
        
        # Obtener todos los detalles actuales de la venta
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles_existentes = session.exec(statement).all()
        
        # Separar paquetes de items normales en el request
        items_paquetes = {}  # {id_paquete: item}
        items_normales = []
        
        for item in venta_request.items:
            if item.id_paquete is not None:
                items_paquetes[item.id_paquete] = item
            else:
                items_normales.append(item)
        
        for detalle in detalles_existentes:
            if detalle.id_paquete is not None:
                # Es un paquete - solo actualizar status si cambió
                if detalle.id_paquete in items_paquetes:
                    nuevo_status = items_paquetes[detalle.id_paquete].status
                    if detalle.status != nuevo_status:
                        detalle.status = nuevo_status
                # No hacer nada si el paquete no viene en el request
            else:
                # No es paquete - eliminar físicamente
                session.delete(detalle)
        
        session.flush()
        
        # Crear solo los nuevos items normales (no paquetes)
        for item in items_normales:
            nuevo_detalle = DetalleVenta(
                id_venta=id_venta,
                cantidad=item.cantidad,
                precio_unitario=Decimal(str(item.precio_unitario)),
                status=item.status,
                id_hamb=item.id_hamb,
                id_cos=item.id_cos,
                id_alis=item.id_alis,
                id_spag=item.id_spag,
                id_papa=item.id_papa,
                id_rec=item.id_rec,
                id_barr=item.id_barr,
                id_maris=item.id_maris,
                id_refresco=item.id_refresco,
                id_paquete=item.id_paquete,
                detalle_paquete=item.detalle_paquete,
                id_magno=item.id_magno,
                id_pizza=item.id_pizza
            )
            session.add(nuevo_detalle)

        session.commit()
        
        respuesta = {
            "Mensaje": "Venta actualizada exitosamente",
            "id_venta": id_venta,
            "tipo_servicio": venta_existente.tipo_servicio
        }
        
        # Agregar información específica según el tipo de servicio
        if venta_request.tipo_servicio == 0:
            respuesta["mesa"] = venta_existente.mesa
        elif venta_request.tipo_servicio == 1:
            respuesta["pagos_registrados"] = pagos_creados
            respuesta["numero_pagos"] = len(pagos_creados)
        elif venta_request.tipo_servicio == 2:
            respuesta["id_cliente"] = venta_request.id_cliente
            respuesta["id_direccion"] = venta_request.id_direccion
        
        if venta_request.nombreClie:
            respuesta["nombreClie"] = venta_request.nombreClie
        
        return respuesta

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la venta: {str(e)}")



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




