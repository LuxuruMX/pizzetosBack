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
                                     PricePaquete,
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
from app.models.paquetesModel import paquete
from app.models.magnoModel import magno
from app.models.pizzasModel import pizzas


router = APIRouter()

@router.get("/hamburguesas", response_model=List[priceHamburguesa])
async def get_price_hamburguesas(
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
async def get_price_alitas(
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
async def get_price_costillas(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
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
async def get_price_spaguetty(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
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
async def get_price_papas(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
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
async def get_price_rectangular(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
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
async def get_price_barra(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
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
async def get_price_mariscos(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
):
    statement = (
        select(mariscos.id_maris, mariscos.nombre, tamanosPizzas.precio, tamanosPizzas.tamano)
        .join(tamanosPizzas, mariscos.id_tamañop == tamanosPizzas.id_tamañop)
        .order_by(mariscos.id_maris)
    )
    result = session.exec(statement).all()
    return [PriceMarisco(
        id_maris=r.id_maris,
        nombre=r.nombre,
        precio=r.precio,
        tamano=r.tamano
    ) for r in result]

@router.get("/refrescos", response_model=List[PriceRefresco])
async def get_price_refrescos(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
):
    statement = (
        select(refrescos.id_refresco, refrescos.nombre, tamanosRefrescos.precio, tamanosRefrescos.tamano)
        .join(tamanosRefrescos, refrescos.id_tamano == tamanosRefrescos.id_tamano)
        .order_by(refrescos.id_refresco)
        .where(refrescos.nombre != "Jarrito")
    )
    result = session.exec(statement).all()
    return [PriceRefresco(
        id_refresco=r.id_refresco,
        nombre=r.nombre,
        precio=r.precio,
        tamano=r.tamano
    ) for r in result]
    
    
@router.get("/paquetes", response_model=List[PricePaquete])
async def get_price_paquete1(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
):
    statement = (
        select(paquete.id_paquete, paquete.nombre, paquete.precio)
        .order_by(paquete.id_paquete)
    )
    result = session.exec(statement).all()
    return [PricePaquete(
        id_paquete=r.id_paquete,
        nombre=r.nombre,
        precio=r.precio
    ) for r in result]


@router.get("/magno", response_model=List[PriceMagno])
async def get_price_magno(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
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

@router.get("/pizzas", response_model=List[PricePizza])
async def get_price_pizzas(
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_venta"))
):
    statement = (
        select(pizzas.id_pizza, especialidad.nombre.label("nombre"), tamanosPizzas.precio, tamanosPizzas.tamano)
        .join(especialidad, pizzas.id_esp == especialidad.id_esp)
        .join(tamanosPizzas, pizzas.id_tamano == tamanosPizzas.id_tamañop)
        .order_by(pizzas.id_pizza)
    
    )
    result = session.exec(statement).all()
    return [PricePizza(
        id_pizza=r.id_pizza,
        nombre=r.nombre,
        precio=r.precio,
        tamano=r.tamano
    ) for r in result]



@router.get("/descripciones", response_model=List[dict])
async def get_descriptions(
    session: Session = Depends(get_session)
):
    # Ejecutar ambas consultas
    statement = select(especialidad.nombre, especialidad.descripcion).order_by(especialidad.id_esp)
    result = session.exec(statement).all()

    statement2 = select(mariscos.nombre, mariscos.descripcion).order_by(mariscos.id_maris)
    result2 = session.exec(statement2).all()

    # Combinar ambos resultados en una sola lista
    combined_results = [
        {"nombre": r.nombre, "descripcion": r.descripcion} for r in result
    ] + [
        {"nombre": r.nombre, "descripcion": r.descripcion} for r in result2
    ]

    return combined_results
