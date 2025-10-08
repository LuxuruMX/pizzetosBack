from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.refrescosModel import refrescos
from app.schemas.refrescosSchema import createRefrescos, readRefrescosOut

from app.models.categoriaModel import categoria as CategoriasProd
from app.models.tamanosRefrescosModel import tamanosRefrescos

router=APIRouter()

@router.get("/", response_model=List[readRefrescosOut])
def getRefrescos(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(refrescos.id_refresco, refrescos.nombre, tamanosRefrescos.tamano.label("tamaño"), CategoriasProd.descripcion.label("categoria"))
        .join(tamanosRefrescos, refrescos.id_tamano == tamanosRefrescos.id_tamano)
        .join(CategoriasProd, refrescos.id_cat == CategoriasProd.id_cat)
    )
    results = session.exec(statement).all()
    return [readRefrescosOut(
        id_refresco=r.id_refresco,
        nombre=r.nombre,
        tamaño=r.tamaño,
        categoria=r.categoria
    ) for r in results]
    
@router.get("/{id_refresco}", response_model=readRefrescosOut)
def getRefrescosById(id_refresco: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(refrescos.id_refresco, refrescos.nombre, tamanosRefrescos.tamano.label("tamaño"), CategoriasProd.descripcion.label("categoria"))
        .join(tamanosRefrescos, refrescos.id_tamano == tamanosRefrescos.id_tamano)
        .join(CategoriasProd, refrescos.id_cat == CategoriasProd.id_cat)
        .where(refrescos.id_refresco == id_refresco)
    )

    result = session.exec(statement).first()
    if result:
        return readRefrescosOut(
            id_refresco=result.id_refresco,
            nombre=result.nombre,
            tamaño=result.tamaño,
            categoria=result.categoria
        )
    return {"message": "Refresco no encontrado"}

@router.put("/{id_refresco}")
def updateRefresco(id_refresco: int, refresco: createRefrescos, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    refri = session.get(refrescos, id_refresco)
    if not refri:
        return {"message": "Refresco no encontrado"}
    refri.nombre = refresco.nombre
    refri.id_tamano = refresco.id_tamano
    refri.id_cat = refresco.id_cat
    session.add(refri)
    session.commit()
    session.refresh(refri)
    return {"message": "Refresco actualizado correctamente"}

@router.post("/")
def createRefresco(refresco: createRefrescos, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    refri=refrescos(
        nombre= refresco.nombre,
        id_tamano= refresco.id_tamano,
        id_cat= refresco.id_cat
    )
    session.add(refri)
    session.commit()
    session.refresh(refri)
    return {"message" : "Refresco registrado correctamente"}

@router.delete("/{id_refresco}")
def deleteRefresco(id_refresco: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    refri = session.get(refrescos, id_refresco)
    if not refri:
        return {"message": "Refresco no encontrado"}
    session.delete(refri)
    session.commit()
    return {"message": "Refresco eliminado correctamente"}