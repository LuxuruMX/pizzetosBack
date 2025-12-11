from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, update
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_session
from app.models.cajaModel import Caja
from app.models.movimientoCajaModel import MovimientoCaja


from app.schemas.cajaSchema import (AperturaCajaRequest,
                                    CierreCajaRequest,
                                    MovimientoCajaRequest,
                                    FlujoCajaResponse)


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



@router.post("/movimiento/{id_caja}")
async def registrar_movimiento_caja(
    id_caja: int,
    movimiento: MovimientoCajaRequest,
    session: Session = Depends(get_session)
):
    caja = session.get(Caja, id_caja)
    if not caja or caja.status != 1:
        raise HTTPException(status_code=404, detail="Caja no encontrada o no está abierta")
    
    nuevo_movimiento = MovimientoCaja(
        id_caja=id_caja,
        tipo_movimiento=movimiento.tipo_movimiento,
        monto=movimiento.monto,
        concepto=movimiento.concepto,
        fecha_hora=datetime.now()
    )
    session.add(nuevo_movimiento)
    session.commit()
    session.refresh(nuevo_movimiento)
    return {"message": "Movimiento registrado exitosamente", "id_movimiento": nuevo_movimiento.id_movimiento}