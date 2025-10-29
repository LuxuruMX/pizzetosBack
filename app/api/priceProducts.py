from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.permissions import require_permission, require_any_permission

from app.schemas.priceSchema import (PriceCostilla,
                                     PriceAlita,
                                     priceHamburguesa,
                                     PriceSpaghetti,
                                     PricePapas,
                                     PriceRectangular,
                                     PriceBarra,
                                     PriceMarisco,
                                     PriceRefresco,
                                     PricePaquete1,
                                     PricePaquete2,
                                     PricePaquete3,
                                     PriceMagno,
                                     PricePizza)

from app.models.especialidadModel import especialidad
from app.models.tamanosPizzasModel import tamanosPizzas
from app.models.tamanosRefrescosModel import tamanosRefrescos

from app.models.costillasModel import costillas
from app.models.alitasModel import alitas
from app.models.hamburguesasModel import hamburguesas
from app.models.spaguettyModel import spaguetty
from app.models.papasModel import papas
from app.models.rectangularModel import rectangular
from app.models.barraModel import barra
from app.models.mariscosModel import mariscos
from app.models.refrescosModel import refrescos
from app.models.paquetesModel import paquete1, paquete2, paquete3
from app.models.magnoModel import magno
from app.models.pizzasModel import pizzas


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
    

@router.get("/spaguetty", response_model=List[PriceSpaghetti])
def get_price_spaguetty(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(spaguetty.id_spag, spaguetty.orden.label("nombre"), spaguetty.precio)
        .order_by(spaguetty.id_spag)
    )
    result = session.exec(statement).all()
    return [PriceSpaghetti(
        id_spag=r.id_spag,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]
    
@router.get("/papas", response_model=List[PricePapas])
def get_price_papas(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(papas.id_papa, papas.orden.label("nombre"), papas.precio)
        .order_by(papas.id_papa)
    )
    result = session.exec(statement).all()
    return [PricePapas(
        id_papa=r.id_papa,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]
    
@router.get("/rectangular", response_model=List[PriceRectangular])
def get_price_rectangular(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(rectangular.id_rec, especialidad.nombre.label("nombre"), rectangular.precio)
        .join(especialidad, rectangular.id_esp == especialidad.id_esp)
        .order_by(rectangular.id_rec)
    )
    result = session.exec(statement).all()
    return [PriceRectangular(
        id_rec=r.id_rec,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]
    
@router.get("/barra", response_model=List[PriceBarra])
def get_price_barra(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(barra.id_barr, especialidad.nombre.label("nombre"), barra.precio)
        .join(especialidad, barra.id_especialidad == especialidad.id_esp)
        .order_by(barra.id_barr)
    )
    result = session.exec(statement).all()
    return [PriceBarra(
        id_barr=r.id_barr,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]
    
@router.get("/mariscos", response_model=List[PriceMarisco])
def get_price_mariscos(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(mariscos.id_maris, mariscos.nombre, tamanosPizzas.precio)
        .join(tamanosPizzas, mariscos.id_tamañop == tamanosPizzas.id_tamañop)
        .order_by(mariscos.id_maris)
    )
    result = session.exec(statement).all()
    return [PriceMarisco(
        id_maris=r.id_maris,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]

@router.get("/refrescos", response_model=List[PriceRefresco])
def get_price_refrescos(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(refrescos.id_refresco, refrescos.nombre, tamanosRefrescos.precio)
        .join(tamanosRefrescos, refrescos.id_tamano == tamanosRefrescos.id_tamano)
        .order_by(refrescos.id_refresco)
    )
    result = session.exec(statement).all()
    return [PriceRefresco(
        id_refresco=r.id_refresco,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]
    
    
@router.get("/paquete1", response_model=List[PricePaquete1])
def get_price_paquete1(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(paquete1.id_paquete1, especialidad.nombre, paquete1.precio)
        .join(especialidad, paquete1.id_especialidad == especialidad.id_esp)
        .order_by(paquete1.id_paquete1)
    
    )
    result = session.exec(statement).all()
    return [PricePaquete1(
        id_paquete1=r.id_paquete1,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]

@router.get("/paquete2", response_model=List[PricePaquete2])
def get_price_paquete2(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(paquete2.id_paquete2, especialidad.nombre, paquete2.precio)
        .join(especialidad, paquete2.id_especialidad == especialidad.id_esp)
        .order_by(paquete2.id_paquete2)
    
    )
    result = session.exec(statement).all()
    return [PricePaquete2(
        id_paquete2=r.id_paquete2,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]

@router.get("/paquete3", response_model=List[PricePaquete3])
def get_price_paquete3(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(paquete3.id_paquete3, especialidad.nombre, paquete3.precio)
        .join(especialidad, paquete3.id_especialidad == especialidad.id_esp)
        .order_by(paquete3.id_paquete3)
    
    )
    result = session.exec(statement).all()
    return [PricePaquete3(
        id_paquete3=r.id_paquete3,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]

@router.get("/magno", response_model=List[PriceMagno])
def get_price_magno(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(magno.id_magno, especialidad.nombre.label("nombre"), magno.precio)
        .join(especialidad, magno.id_especialidad == especialidad.id_esp)
        .order_by(magno.id_magno)
    
    )
    result = session.exec(statement).all()
    return [PriceMagno(
        id_magno=r.id_magno,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]

@router.get("/pizzas")
def get_price_pizzas(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_producto"))
):
    statement = (
        select(pizzas.id_pizza, especialidad.nombre.label("nombre"), tamanosPizzas.precio)
        .join(especialidad, pizzas.id_esp == especialidad.id_esp)
        .join(tamanosPizzas, pizzas.id_tamano == tamanosPizzas.id_tamañop)
        .order_by(pizzas.id_pizza)
    
    )
    result = session.exec(statement).all()
    return [PricePizza(
        id_pizza=r.id_pizza,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]