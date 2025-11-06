from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_session
from app.models.detallesModel import DetalleVenta
from app.models.ventaModel import Venta
from app.schemas.ventaSchema import VentaRequest, VentaResponse

from app.models.clienteModel import Cliente
from app.models.sucursalModel import Sucursal

router = APIRouter()


@router.get("/pedidos-cocina")
async def listar_pedidos_cocina(
    session: Session = Depends(get_session),
    filtro: str = "hoy",
    status: Optional[int] = None,
    id_suc: Optional[int] = None,
):
    """
    Endpoint para mostrar pedidos activos en cocina.
    Por defecto excluye pedidos completados (status=2).
    
    Parámetros de status:
    - None (default): Muestra Esperando (0) y Preparando (1)
    - 0: Solo Esperando
    - 1: Solo Preparando
    """
    try:
        # Construir query base
        statement = select(Venta).order_by(Venta.fecha_hora.asc())

        # Filtro por fecha
        if filtro == "hoy":
            hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = hoy_inicio + timedelta(days=1)
            statement = statement.where(
                Venta.fecha_hora >= hoy_inicio,
                Venta.fecha_hora < hoy_fin
            )

        # Filtro por status
        if status is not None:
            # Si se especifica un status, solo mostrar ese
            statement = statement.where(Venta.status == status)
        else:
            # Por defecto, solo mostrar Esperando (0) y Preparando (1)
            statement = statement.where(Venta.status.in_([0, 1]))

        # Filtro por sucursal
        if id_suc:
            statement = statement.where(Venta.id_suc == id_suc)

        ventas = session.exec(statement).all()

        pedidos_cocina = []
        for venta in ventas:
            # Obtener cliente
            cliente = session.get(Cliente, venta.id_cliente)
            nombre_cliente = cliente.nombre if cliente else "Desconocido"

            # Obtener sucursal
            sucursal = session.get(Sucursal, venta.id_suc)
            nombre_sucursal = sucursal.nombre if sucursal else "Desconocida"

            # Obtener detalles de productos
            statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == venta.id_venta)
            detalles = session.exec(statement_detalles).all()

            # Construir lista de productos con nombres
            productos = []
            for det in detalles:
                producto_info = {
                    "cantidad": det.cantidad,
                    "precio_unitario": float(det.precio_unitario),
                    "subtotal": float(det.cantidad * det.precio_unitario),
                    "nombre": None,
                    "tipo": None
                }

                if det.id_pizza:
                    from app.models.pizzasModel import pizzas
                    producto = session.get(pizzas, det.id_pizza)
                    if producto:
                        try:
                            from app.models.especialidadModel import especialidad
                            especialidad_obj = session.get(especialidad, producto.id_esp)
                            nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                        except:
                            nombre_especialidad = f"Especialidad #{producto.id_esp}"

                        producto_info["nombre"] = nombre_especialidad
                        producto_info["tipo"] = "Pizza"
                    
                elif det.id_hamb:
                    from app.models.hamburguesasModel import hamburguesas
                    producto = session.get(hamburguesas, det.id_hamb)
                    if producto:
                        producto_info["nombre"] = producto.paquete
                        producto_info["tipo"] = "Hamburguesa"
                
                elif det.id_cos:
                    from app.models.costillasModel import costillas
                    producto = session.get(costillas, det.id_cos)
                    if producto:
                        producto_info["nombre"] = producto.orden
                        producto_info["tipo"] = "Costilla"
                
                elif det.id_alis:
                    from app.models.alitasModel import alitas
                    producto = session.get(alitas, det.id_alis)
                    if producto:
                        producto_info["nombre"] = producto.orden
                        producto_info["tipo"] = "Alitas"
                
                elif det.id_spag:
                    from app.models.spaguettyModel import spaguetty
                    producto = session.get(spaguetty, det.id_spag)
                    if producto:
                        producto_info["nombre"] = producto.orden
                        producto_info["tipo"] = "Spaghetti"
                
                elif det.id_papa:
                    from app.models.papasModel import papas
                    producto = session.get(papas, det.id_papa)
                    if producto:
                        producto_info["nombre"] = producto.orden
                        producto_info["tipo"] = "Papas"
                
                elif det.id_maris:
                    from app.models.mariscosModel import mariscos
                    producto = session.get(mariscos, det.id_maris)
                    if producto:
                        producto_info["nombre"] = producto.nombre
                        producto_info["tipo"] = "Mariscos"
                
                elif det.id_refresco:
                    from app.models.refrescosModel import refrescos
                    producto = session.get(refrescos, det.id_refresco)
                    if producto:
                        producto_info["nombre"] = producto.nombre
                        producto_info["tipo"] = "Refresco"
                
                elif det.id_magno:
                    from app.models.magnoModel import magno
                    producto = session.get(magno, det.id_magno)
                    if producto:
                        try:
                            from app.models.especialidadModel import especialidad
                            especialidad_obj = session.get(especialidad, producto.id_especialidad)
                            nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                        except:
                            nombre_especialidad = f"Especialidad #{producto.id_especialidad}"

                        producto_info["nombre"] = nombre_especialidad
                        producto_info["tipo"] = "Magno"
                
                elif det.id_rec:
                    from app.models.rectangularModel import rectangular
                    producto = session.get(rectangular, det.id_rec)
                    if producto:
                        try:
                            from app.models.especialidadModel import especialidad
                            especialidad_obj = session.get(especialidad, producto.id_esp)
                            nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                        except:
                            nombre_especialidad = f"Especialidad #{producto.id_esp}"

                        producto_info["nombre"] = nombre_especialidad
                        producto_info["tipo"] = "Rectangular"

                productos.append(producto_info)

            total_items = sum(det.cantidad for det in detalles)
            
            # Calcular tiempo transcurrido
            tiempo_transcurrido = datetime.now() - venta.fecha_hora
            minutos_transcurridos = int(tiempo_transcurrido.total_seconds() / 60)

            pedidos_cocina.append({
                "id_venta": venta.id_venta,
                "fecha_hora": venta.fecha_hora,
                "tiempo_transcurrido_minutos": minutos_transcurridos,
                "cliente": nombre_cliente,
                "sucursal": nombre_sucursal,
                "status": venta.status,
                "status_texto": {
                    0: "Esperando",
                    1: "Preparando",
                    2: "Completado"
                }.get(venta.status, "Desconocido"),
                "total": float(venta.total),
                "cantidad_items": total_items,
                "cantidad_productos_diferentes": len(detalles),
                "productos": productos
            })

        return {
            "pedidos": pedidos_cocina,
            "total": len(pedidos_cocina),
            "filtro_aplicado": filtro,
            "status_filtrado": status,
            "sucursal_filtrada": id_suc
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")

@router.get("/pedidos-cocina/{id_venta}/detalle")
async def obtener_detalle_pedido_cocina(
    id_venta: int,
    session: Session = Depends(get_session)
):
    """
    Obtiene el detalle completo de un pedido para mostrar en modal.
    Incluye toda la información de productos y cliente.
    """
    try:
        # Obtener venta
        venta = session.get(Venta, id_venta)
        if not venta:
            raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")

        # Obtener cliente
        cliente = session.get(Cliente, venta.id_cliente)
        nombre_cliente = cliente.nombre if cliente else "Desconocido"

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
                "precio_unitario": float(det.precio_unitario),
                "subtotal": float(det.cantidad * det.precio_unitario),
                "nombre": None,
                "tipo": None
            }

            if det.id_pizza:
                from app.models.pizzasModel import pizzas
                producto = session.get(pizzas, det.id_pizza)
                if producto:
                    try:
                        from app.models.especialidadModel import especialidad
                        especialidad_obj = session.get(especialidad, producto.id_esp)
                        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                    except:
                        nombre_especialidad = f"Especialidad #{producto.id_esp}"
                    producto_info["nombre"] = nombre_especialidad
                    producto_info["tipo"] = "Pizza"
                
            elif det.id_hamb:
                from app.models.hamburguesasModel import hamburguesas
                producto = session.get(hamburguesas, det.id_hamb)
                if producto:
                    producto_info["nombre"] = producto.paquete
                    producto_info["tipo"] = "Hamburguesa"
            
            elif det.id_cos:
                from app.models.costillasModel import costillas
                producto = session.get(costillas, det.id_cos)
                if producto:
                    producto_info["nombre"] = producto.orden
                    producto_info["tipo"] = "Costilla"
            
            elif det.id_alis:
                from app.models.alitasModel import alitas
                producto = session.get(alitas, det.id_alis)
                if producto:
                    producto_info["nombre"] = producto.orden
                    producto_info["tipo"] = "Alitas"
            
            elif det.id_spag:
                from app.models.spaguettyModel import spaguetty
                producto = session.get(spaguetty, det.id_spag)
                if producto:
                    producto_info["nombre"] = producto.orden
                    producto_info["tipo"] = "Spaghetti"
            
            elif det.id_papa:
                from app.models.papasModel import papas
                producto = session.get(papas, det.id_papa)
                if producto:
                    producto_info["nombre"] = producto.orden
                    producto_info["tipo"] = "Papas"
            
            elif det.id_maris:
                from app.models.mariscosModel import mariscos
                producto = session.get(mariscos, det.id_maris)
                if producto:
                    producto_info["nombre"] = producto.nombre
                    producto_info["tipo"] = "Mariscos"
            
            elif det.id_refresco:
                from app.models.refrescosModel import refrescos
                producto = session.get(refrescos, det.id_refresco)
                if producto:
                    producto_info["nombre"] = producto.nombre
                    producto_info["tipo"] = "Refresco"
            
            elif det.id_magno:
                from app.models.magnoModel import magno
                producto = session.get(magno, det.id_magno)
                if producto:
                    try:
                        from app.models.especialidadModel import especialidad
                        especialidad_obj = session.get(especialidad, producto.id_especialidad)
                        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                    except:
                        nombre_especialidad = f"Especialidad #{producto.id_especialidad}"
                    producto_info["nombre"] = nombre_especialidad
                    producto_info["tipo"] = "Magno"
            
            elif det.id_rec:
                from app.models.rectangularModel import rectangular
                producto = session.get(rectangular, det.id_rec)
                if producto:
                    try:
                        from app.models.especialidadModel import especialidad
                        especialidad_obj = session.get(especialidad, producto.id_esp)
                        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                    except:
                        nombre_especialidad = f"Especialidad #{producto.id_esp}"
                    producto_info["nombre"] = nombre_especialidad
                    producto_info["tipo"] = "Rectangular"

            productos.append(producto_info)

        total_items = sum(det.cantidad for det in detalles)
        tiempo_transcurrido = datetime.now() - venta.fecha_hora
        minutos_transcurridos = int(tiempo_transcurrido.total_seconds() / 60)

        return {
            "id_venta": venta.id_venta,
            "fecha_hora": venta.fecha_hora,
            "tiempo_transcurrido_minutos": minutos_transcurridos,
            "cliente": nombre_cliente,
            "sucursal": nombre_sucursal,
            "status": venta.status,
            "status_texto": {
                0: "Esperando",
                1: "Preparando",
                2: "Completado"
            }.get(venta.status, "Desconocido"),
            "total": float(venta.total),
            "cantidad_items": total_items,
            "cantidad_productos_diferentes": len(detalles),
            "productos": productos
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalle del pedido: {str(e)}")

@router.post("/")
async def crear_venta(
    venta_request: VentaRequest,
    session: Session = Depends(get_session)
):
    if not venta_request.items:
        raise HTTPException(status_code=400, detail="La venta debe contener al menos un item")

    cliente = session.get(Cliente, venta_request.id_cliente)
    if not cliente:
        raise HTTPException(status_code=404, detail=f"Cliente con ID {venta_request.id_cliente} no encontrado")

    sucursal = session.get(Sucursal, venta_request.id_suc)
    if not sucursal:
        raise HTTPException(status_code=404, detail=f"Sucursal con ID {venta_request.id_suc} no encontrada")

    try:
        nueva_venta = Venta(
            id_suc=venta_request.id_suc,
            id_cliente=venta_request.id_cliente,
            fecha_hora=datetime.now(),
            total=Decimal(str(venta_request.total))
        )
        session.add(nueva_venta)
        session.flush()

        for item in venta_request.items:
            nuevo_detalle = DetalleVenta(
                id_venta=nueva_venta.id_venta,
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
                id_paquete1=item.id_paquete1,
                id_paquete2=item.id_paquete2,
                id_paquete3=item.id_paquete3,
                id_magno=item.id_magno,
                id_pizza=item.id_pizza
            )
            session.add(nuevo_detalle)

        session.commit()

        venta_actualizada = session.get(Venta, nueva_venta.id_venta)
        
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == nueva_venta.id_venta)
        detalles_db = session.exec(statement).all()
        
        detalles_respuesta = []
        for det in detalles_db:
            subtotal = det.cantidad * det.precio_unitario
            detalles_respuesta.append({
                "cantidad": det.cantidad,
                "precio_unitario": float(det.precio_unitario),
                "subtotal": float(subtotal)
            })

        return {"Mensaje": "Venta creada exitosamente"}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la venta: {str(e)}")
    
    
    
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
    
@router.put("/{id_venta}", response_model=VentaResponse)
async def editar_venta(
    id_venta: int,
    venta_request: VentaRequest,
    session: Session = Depends(get_session)
):
    
    # Validar que la venta existe
    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    if not venta_request.items:
        raise HTTPException(status_code=400, detail="La venta debe contener al menos un item")
    
    # Validar cliente si cambió
    if venta_request.id_cliente != venta.id_cliente:
        cliente = session.get(Cliente, venta_request.id_cliente)
        if not cliente:
            raise HTTPException(status_code=404, detail=f"Cliente con ID {venta_request.id_cliente} no encontrado")
    
    # Validar sucursal si cambió
    if venta_request.id_suc != venta.id_suc:
        sucursal = session.get(Sucursal, venta_request.id_suc)
        if not sucursal:
            raise HTTPException(status_code=404, detail=f"Sucursal con ID {venta_request.id_suc} no encontrada")
    
    try:
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles_antiguos = session.exec(statement).all()
        for detalle in detalles_antiguos:
            session.delete(detalle)
        
        total_calculado = sum(
            Decimal(str(item.precio_unitario)) * item.cantidad 
            for item in venta_request.items
        )
        
        venta.id_suc = venta_request.id_suc
        venta.id_cliente = venta_request.id_cliente
        venta.total = total_calculado
        session.add(venta)
        session.flush()
        
        for item in venta_request.items:
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
                id_paquete1=item.id_paquete1,
                id_paquete2=item.id_paquete2,
                id_paquete3=item.id_paquete3,
                id_magno=item.id_magno,
            )
            session.add(nuevo_detalle)
        
        session.commit()
        
        venta_actualizada = session.get(Venta, id_venta)
        
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles_db = session.exec(statement).all()
        
        detalles_respuesta = []
        for det in detalles_db:
            subtotal = det.cantidad * det.precio_unitario
            detalles_respuesta.append({
                "cantidad": det.cantidad,
                "precio_unitario": float(det.precio_unitario),
                "subtotal": float(subtotal)
            })
        
        return {"Mensaje": "Venta actualizada exitosamente"}
    
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
        
        venta.status = 2
        session.add(venta)
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