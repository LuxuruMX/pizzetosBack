from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.permissions import require_permission, require_any_permission

from app.models.spaguettyModel import spaguetty
from app.schemas.spaguettySchema import readSpaguettyOut, createSpaguetty

from app.models.categoriaModel import categoria as CategoriasProd

router = APIRouter()

@router.get("/", response_model=List[readSpaguettyOut])
def getSpaguetty(session: Session = Depends(get_session), _: None = Depends(require_permission("ver_producto"))):
    statement = (
        select(spaguetty.id_spag, spaguetty.orden, spaguetty.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, spaguetty.id_cat == CategoriasProd.id_cat)
    )

    results = session.exec(statement).all()
    return [readSpaguettyOut(
        id_spag=r.id_spag,
        orden=r.orden,
        precio=r.precio,
        categoria=r.categoria
    ) for r in results]
    
@router.get("/{id_spag}", response_model=readSpaguettyOut)
def getSpaguettyById(id_spag: int, session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_producto", "modificar_producto"))):
    statement = (
        select(spaguetty.id_spag, spaguetty.orden, spaguetty.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, spaguetty.id_cat == CategoriasProd.id_cat)
        .where(spaguetty.id_spag == id_spag)
    )

    result = session.exec(statement).first()
    if result:
        return readSpaguettyOut(
            id_spag=result.id_spag,
            orden=result.orden,
            precio=result.precio,
            categoria=result.categoria
        )
    return {"message": "Spaguetty no encontrado"}

@router.put("/{id_spag}")
def updateSpaguetty(id_spag: int, spaguetty_data: createSpaguetty, session: Session = Depends(get_session), _: None = Depends(require_permission("modificar_producto"))):
    spag = session.get(spaguetty, id_spag)
    if not spag:
        return {"message": "Spaguetty no encontrado"}
    spag.orden = spaguetty_data.orden
    spag.precio = spaguetty_data.precio
    spag.id_cat = spaguetty_data.id_cat
    session.add(spag)
    session.commit()
    session.refresh(spag)
    return {"message": "Spaguetty actualizado correctamente"}

@router.post("/", response_model=createSpaguetty)
def createSpaguettyItem(spaguetty_data: createSpaguetty, session: Session = Depends(get_session), _: None = Depends(require_permission("crear_producto"))):
    new_spag = spaguetty(
        orden=spaguetty_data.orden,
        precio=spaguetty_data.precio,
        id_cat=spaguetty_data.id_cat
    )
    session.add(new_spag)
    session.commit()
    session.refresh(new_spag)
    return new_spag

@router.delete("/{id_spag}")
def deleteSpaguetty(id_spag: int, session: Session = Depends(get_session), _: None = Depends(require_permission("eliminar_producto"))):
    spag = session.get(spaguetty, id_spag)
    if not spag:
        return {"message": "Spaguetty no encontrado"}
    session.delete(spag)
    session.commit()
    return {"message": "Spaguetty eliminado correctamente"}