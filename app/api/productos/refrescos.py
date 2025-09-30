from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.refrescosModel import refrescos
from app.schemas.refrescosSchema import createRefrescos, readRefrescosOut

from app.models.categoriaModel import categoria as CategoriasProd

router=APIRouter()

@router.get("/refrescos", response_model=List[readRefrescosOut] ,tags=["Refrescos"])
def getRefrescos(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=(
        select(refrescos.id_refresco, refrescos.nombre, refrescos.id_tamano, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, refrescos.id_cat == CategoriasProd.id_cat)
    )
    results = session.exec(statement).all()
    return [readRefrescosOut(
        id_refresco=r.id_refresco,
        nombre=r.nombre,
        tamano=r.id_tamano,
        categoria=r.categoria
    ) for r in results]
    
@router.get("/refrescos/{id_refresco}", response_model=readRefrescosOut, tags=["Refrescos"])
def getRefrescoById(id_refresco: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(refrescos.id_refresco, refrescos.nombre, refrescos.id_tamano, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, refrescos.id_cat == CategoriasProd.id_cat)
        .where(refrescos.id_refresco == id_refresco)
    )

    result = session.exec(statement).first()
    if result:
        return readRefrescosOut(
            id_refresco=result.id_refresco,
            nombre=result.nombre,
            tamano=result.id_tamano,
            categoria=result.categoria
        )
    return {"message": "Refresco no encontrado"}

@router.put("/actualizar-refresco/{id_refresco}", tags=["Refrescos"])
def updateRefresco(id_refresco: int, refresco_data: createRefrescos, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    refresco_item = session.get(refrescos, id_refresco)
    if not refresco_item:
        return {"message": "Refresco no encontrado"}
    
    refresco_item.nombre = refresco_data.nombre
    refresco_item.id_tamano = refresco_data.id_tamano
    refresco_item.id_cat = refresco_data.id_cat
    
    session.add(refresco_item)
    session.commit()
    session.refresh(refresco_item)
    
    return {"message": "Refresco actualizado correctamente"}

@router.post("/crear-refresco", tags=["Refrescos"])
def createRefresco(refresco_data: createRefrescos, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    nuevo_refresco = refrescos(
        nombre= refresco_data.nombre,
        id_tamano= refresco_data.id_tamano,
        id_cat= refresco_data.id_cat
    )
    session.add(nuevo_refresco)
    session.commit()
    session.refresh(nuevo_refresco)
    return {"message": "Refresco registrado correctamente"}

@router.delete("/eliminar-refresco/{id_refresco}", tags=["Refrescos"])
def deleteRefresco(id_refresco: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    
    refresco_item = session.get(refrescos, id_refresco)
    if not refresco_item:
        return {"message": "Refresco no encontrado"}
    session.delete(refresco_item)
    session.commit()
    return {"message": "Refresco eliminado correctamente"}