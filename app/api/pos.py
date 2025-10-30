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
        # Usar el total que viene del frontend (ya incluye descuentos/promociones)
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
        # 1️⃣ Eliminar todos los detalles antiguos
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles_antiguos = session.exec(statement).all()
        for detalle in detalles_antiguos:
            session.delete(detalle)
        
        # 2️⃣ Calcular el nuevo total desde los items recibidos
        total_calculado = sum(
            Decimal(str(item.precio_unitario)) * item.cantidad 
            for item in venta_request.items
        )
        
        # 3️⃣ Actualizar datos de la venta
        venta.id_suc = venta_request.id_suc
        venta.id_cliente = venta_request.id_cliente
        venta.total = total_calculado
        session.add(venta)
        session.flush()
        
        # 4️⃣ Crear nuevos detalles
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
        
        # 5️⃣ Obtener venta actualizada
        venta_actualizada = session.get(Venta, id_venta)
        
        # 6️⃣ Obtener detalles actualizados
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
        # Eliminar detalles primero (por la FK)
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
        statement = select(Venta).order_by(Venta.fecha_hora.desc())

        # Filtrar por fecha si es "hoy"
        if filtro == "hoy":
            hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = hoy_inicio + timedelta(days=1)
            statement = statement.where(
                Venta.fecha_hora >= hoy_inicio,
                Venta.fecha_hora < hoy_fin
            )

        if status is not None:
            statement = statement.where(Venta.status == status)

        # Filtrar por sucursal si se especifica
        if id_suc:
            statement = statement.where(Venta.id_suc == id_suc)

        # Ejecutar query
        ventas = session.exec(statement).all()

        # Construir respuesta resumida
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
    
    
    
@router.patch("/{id_venta}")
async def actualizar_status_venta(
    id_venta: int,
    status: int,
    session: Session = Depends(get_session)
):
    # Validar que el status esté en un rango permitido
    if status not in [0, 1, 2]:
        raise HTTPException(
            status_code=400,
            detail="Status inválido. Debe ser 0, 1 o 2."
        )
    
    # Obtener venta
    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    try:
        # Actualizar solo el status
        venta.status = status
        session.add(venta)
        session.commit()
        session.refresh(venta)
        
        return {"Message": "Status actualizado exitosamente"}
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar status: {str(e)}")