from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from decimal import Decimal
from datetime import datetime

from app.db.session import get_session
from app.models.cajaModel import Caja
from app.models.ventaModel import Venta
from app.models.pagosModel import Pago

from app.models.empleadoModel import Empleados


from app.schemas.cajaSchema import (AperturaCajaRequest,
                                    CierreCajaRequest,
                                    CajaDetalleResponse)


router = APIRouter()

@router.post("/abrir")
async def abrir_caja(
    apertura: AperturaCajaRequest,
    session: Session = Depends(get_session)
):
    nueva_caja = Caja(
        id_suc=apertura.id_suc,
        id_emp=apertura.id_emp,
        fecha_apertura=datetime.now(),
        monto_inicial=apertura.monto_inicial,
        observaciones_apertura=apertura.observaciones_apertura,
        status=1  # Abierta
    )
    session.add(nueva_caja)
    session.commit()
    session.refresh(nueva_caja)
    return {"message": "Caja abierta exitosamente", "id_caja": nueva_caja.id_caja}



@router.patch("/cerrar/{id_caja}")
async def cerrar_caja(
    id_caja: int,
    cierre: CierreCajaRequest,
    session: Session = Depends(get_session)
):
    caja = session.get(Caja, id_caja)
    if not caja or caja.status != 1:
        raise HTTPException(status_code=404, detail="Caja no encontrada o ya cerrada")
    
    caja.fecha_cierre = datetime.now()
    caja.monto_final = cierre.monto_final
    caja.observaciones_cierre = cierre.observaciones_cierre
    caja.status = 2  # Cerrada
    
    session.add(caja)
    session.commit()
    return {"message": "Caja cerrada exitosamente"}


@router.get("/detalles/{id_caja}", response_model=CajaDetalleResponse)
async def obtener_detalle_caja(id_caja: int, session: Session = Depends(get_session)):

    caja = session.exec(
        select(Caja).where(Caja.id_caja == id_caja)
    ).first()

    if not caja:
        raise HTTPException(status_code=404, detail="Caja no encontrada")

    # 2. Obtener el nombre del empleado que abrió la caja
    empleado = session.exec(
        select(Empleados.nickName).where(Empleados.id_emp == caja.id_emp)
    ).first()

    if not empleado:
        # Si no encuentra el empleado, puede usar un valor por defecto o lanzar error
        usuario_apertura = "Empleado Desconocido"
    else:
        usuario_apertura = empleado

    # 3. Calcular totales desde Ventas
    ventas_totales = session.exec(
        select(
            func.count(Venta.id_venta).label('numero_ventas'),
            func.sum(Venta.total).label('total_ventas')
        )
        .where(Venta.id_caja == id_caja)
    ).first()

    numero_ventas = ventas_totales.numero_ventas or 0
    total_ventas_raw = ventas_totales.total_ventas
    total_ventas = float(total_ventas_raw) if isinstance(total_ventas_raw, Decimal) else (total_ventas_raw or 0.0)

    totales_pago = session.exec(
        select(
            Pago.id_metpago,
            func.sum(Pago.monto).label('monto_total')
        )
        .join(Venta, Pago.id_venta == Venta.id_venta) # Join para filtrar por caja
        .where(Venta.id_caja == id_caja)
        .group_by(Pago.id_metpago)
    ).all()

    total_efectivo = 0.0
    total_tarjeta = 0.0
    total_transferencia = 0.0

    for row in totales_pago:
        monto_total = float(row.monto_total) if isinstance(row.monto_total, Decimal) else (row.monto_total or 0.0)
        if row.id_metpago == 2:
            total_efectivo = monto_total
        elif row.id_metpago == 1:
            total_tarjeta = monto_total
        elif row.id_metpago == 3:
            total_transferencia = monto_total


    estado = "cerrada" if caja.fecha_cierre else "abierta"


    respuesta = CajaDetalleResponse(
        id_caja=caja.id_caja,
        fecha_apertura=caja.fecha_apertura,
        estado=estado,
        usuario_apertura=usuario_apertura,
        monto_inicial=float(caja.monto_inicial) if isinstance(caja.monto_inicial, Decimal) else (caja.monto_inicial or 0.0),
        total_ventas=total_ventas,
        numero_ventas=numero_ventas,
        total_efectivo=total_efectivo,
        total_tarjeta=total_tarjeta,
        total_transferencia=total_transferencia
    )

    return respuesta