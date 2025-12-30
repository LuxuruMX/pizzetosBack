from collections import defaultdict

from app.models.empleadoModel import Empleados
from app.models.sucursalModel import Sucursal
from app.models.cajaModel import Caja

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from app.db.session import get_session
from app.models.ventaModel import Venta
from app.models.pagosModel import Pago, MetodosPago
from app.core.permissions import require_any_permission

from app.schemas.corteSchema import (ResumenDia,
                                     SucursalDiaDetalle,
                                     CajaDiaDetalle,
                                     PagoVentaDetalle)

router = APIRouter()





@router.get("/resumen-mes", response_model=List[ResumenDia])
async def get_resumen_mes(
    mes: Optional[int] = Query(None),
    anio: Optional[int] = Query(None),
    id_suc: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):

    # Si no se especifica mes y año, usar el mes actual
    hoy = datetime.now()
    if mes is None:
        mes = hoy.month
    if anio is None:
        anio = hoy.year
    
    # Obtener todas las ventas del mes especificado
    statement = select(Venta, Pago, MetodosPago).outerjoin(
        Pago, Venta.id_venta == Pago.id_venta
    ).outerjoin(
        MetodosPago, Pago.id_metpago == MetodosPago.id_metpago
    ).where(
        func.year(Venta.fecha_hora) == anio,
        func.month(Venta.fecha_hora) == mes
    )
    
    if id_suc is not None:
        statement = statement.where(Venta.id_suc == id_suc)
    
    results = session.exec(statement).all()
    
    # Crear un diccionario para agrupar por día
    dias_data = {}
    
    for venta, pago, metodo in results:
        dia = venta.fecha_hora.day
        
        if dia not in dias_data:
            dias_data[dia] = {
                "efectivo": Decimal("0"),
                "tarjeta": Decimal("0"),
                "transferencia": Decimal("0")
            }
        
        # Si hay pago asociado, sumar el monto al método correspondiente
        if pago and metodo:
            metodo_nombre = metodo.metodo.lower()
            if metodo_nombre in dias_data[dia]:
                dias_data[dia][metodo_nombre] += pago.monto
    
    # Crear la respuesta ordenada por día
    respuesta = []
    for dia in sorted(dias_data.keys()):
        respuesta.append(ResumenDia(
            dia=dia,
            efectivo=dias_data[dia]["efectivo"],
            tarjeta=dias_data[dia]["tarjeta"],
            transferencia=dias_data[dia]["transferencia"]
        ))
    
    return respuesta


@router.get("/reporte-dia", response_model=List[SucursalDiaDetalle])
async def get_reporte_dia(
    fecha: datetime = Query(..., description="Fecha del día a consultar (YYYY-MM-DD)"),
    session: Session = Depends(get_session)
):
    # Limitar a ese día
    inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
    fin = inicio + timedelta(days=1)

    # Buscar todas las sucursales
    sucursales = session.exec(select(Sucursal)).all()
    suc_map = {suc.id_suc: suc.nombre for suc in sucursales}

    # Buscar cajas abiertas ese día
    cajas_stmt = select(Caja).where(Caja.fecha_apertura >= inicio, Caja.fecha_apertura < fin)
    cajas = session.exec(cajas_stmt).all()

    # Buscar empleados de las cajas
    empleados_ids = {caja.id_emp for caja in cajas}
    empleados = session.exec(select(Empleados).where(Empleados.id_emp.in_(empleados_ids))).all() if empleados_ids else []
    emp_map = {emp.id_emp: emp.nombre for emp in empleados}

    # Agrupar cajas por sucursal
    cajas_por_suc = defaultdict(list)
    for caja in cajas:
        cajas_por_suc[caja.id_suc].append(CajaDiaDetalle(
            id_caja=caja.id_caja,
            empleado=emp_map.get(caja.id_emp, "Desconocido"),
            hora_apertura=caja.fecha_apertura,
            hora_cierre=caja.fecha_cierre,
            observaciones_apertura=caja.observaciones_apertura,
            observaciones_cierre=caja.observaciones_cierre
        ))

    # Buscar pagos/ventas de ese día
    pagos_stmt = select(Pago, Venta, MetodosPago).join(
        Venta, Pago.id_venta == Venta.id_venta
    ).join(
        MetodosPago, Pago.id_metpago == MetodosPago.id_metpago
    ).where(
        Venta.fecha_hora >= inicio,
        Venta.fecha_hora < fin
    )
    pagos = session.exec(pagos_stmt).all()

    pagos_por_suc = defaultdict(list)
    for pago, venta, metpago in pagos:
        pagos_por_suc[venta.id_suc].append(PagoVentaDetalle(
            id_venta=venta.id_venta,
            dia=venta.fecha_hora.day,
            metodo_pago=metpago.metodo,
            referencia=pago.referencia,
            monto=pago.monto,
            id_caja=venta.id_caja
        ))

    # Construir respuesta agrupada por sucursal
    respuesta = []
    for id_suc, nombre in suc_map.items():
        respuesta.append(SucursalDiaDetalle(
            sucursal=nombre,
            cajas=cajas_por_suc.get(id_suc, []),
            pagos=pagos_por_suc.get(id_suc, [])
        ))

    return respuesta