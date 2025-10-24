from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.permissions import require_permission, require_any_permission

from app.schemas.priceSchema import PriceCostilla, PriceAlita, priceHamburguesa

from app.models.costillasModel import costillas
from app.models.alitasModel import alitas
from app.models.hamburguesasModel import hamburguesas


router = APIRouter()

@router.get("/hamburguesas", response_model=List[priceHamburguesa])
def get_price_hamburguesas(
    session: Session = Depends(get_session)
):
    statement = (
        select(hamburguesas.id_hamb, hamburguesas.paquete.label("nombre"), hamburguesas.precio)
        .order_by(hamburguesas.id_hamb)
    )
    result = session.exec(statement).all()
    return [priceHamburguesa(
        id_hamb=r.id_hamb,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]


@router.get("/alitas", response_model=List[PriceAlita])
def get_price_alitas(
    session: Session = Depends(get_session)
):
    statement = (
        select(alitas.id_alis, alitas.orden.label("nombre"), alitas.precio)
        .order_by(alitas.id_alis)
    )
    result = session.exec(statement).all()
    return [PriceAlita(
        id_alis=r.id_alis,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]


@router.get("/costillas", response_model=List[PriceCostilla])
def get_price_costillas(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(costillas.id_cos, costillas.orden.label("nombre"), costillas.precio)
        .order_by(costillas.id_cos)
    )
    result = session.exec(statement).all()
    return [PriceCostilla(
        id_cos=r.id_cos,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]