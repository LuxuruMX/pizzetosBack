from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.ventaModel import Venta
from app.schemas.ventaSchema import readVenta, createVenta
from app.core.dependency import verify_token



router=APIRouter()

@router.get("/", response_model=List[readVenta])
def getVentas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(Venta)
    results = session.exec(statement).all()
    return results

@router.post("/crear-venta")
def createVenta(ventas: createVenta, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    venta=Venta(
        id_suc= ventas.id_suc,
        id_cliente=ventas.id_cliente,
        total=ventas.total
    )
    session.add(venta)
    session.commit()
    session.refresh(venta)
    return {"message" : "Venta registrada correctamente"}