from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import BaseModel
from app.db.session import get_session
from app.models.ventaModel import Venta
from app.models.pagosModel import Pago, MetodosPago
from app.core.permissions import require_any_permission

router = APIRouter()


class ResumenDia(BaseModel):
    dia: int
    efectivo: Decimal
    tarjeta: Decimal
    transferencia: Decimal


@router.get("/resumen-mes", tags=["Corte"], response_model=List[ResumenDia])
async def get_resumen_mes(
    mes: Optional[int] = Query(None),
    anio: Optional[int] = Query(None),
    id_suc: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    """
    Obtiene el resumen de ventas por día, desglosadas por método de pago.
    Si no se especifica mes y año, usa el mes actual.
    """
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

