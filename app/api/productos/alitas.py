from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.permissions import require_permission, require_any_permission

from app.models.alitasModel import alitas as Alita
from app.schemas.alitasSchema import readAlitasOut, createAlitas

from app.models.categoriaModel import categoria as CategoriasProd

router = APIRouter()

@router.get("/", response_model=List[readAlitasOut])
def getAlitas(
    session: Session = Depends(get_session), 
    _: None = Depends(require_permission("ver_producto"))  # ← Permiso para VER
):
    statement = (
        select(Alita.id_alis, Alita.orden, Alita.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, Alita.id_cat == CategoriasProd.id_cat)
    )

    results = session.exec(statement).all()
    return [readAlitasOut(
        id_alis=r.id_alis,
        orden=r.orden,
        precio=r.precio,
        categoria=r.categoria
    ) for r in results]
    
    
@router.get("/{id_alis}", response_model=readAlitasOut)
def getAlitasById(id_alis: int, session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_producto", "modificar_producto"))):
    statement = (
        select(Alita.id_alis, Alita.orden, Alita.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, Alita.id_cat == CategoriasProd.id_cat)
        .where(Alita.id_alis == id_alis)
    )

    result = session.exec(statement).first()
    if result:
        return readAlitasOut(
            id_alis=result.id_alis,
            orden=result.orden,
            precio=result.precio,
            categoria=result.categoria
        )
    return {"message": "Alitas no encontradas"}
    
    
@router.put("/{id_alis}")
def updateAlitas(id_alis: int, alitas: createAlitas, session: Session = Depends(get_session), _: None = Depends(require_permission("modificar_producto"))):
    alita = session.get(Alita, id_alis)
    if not alita:
        return {"message": "Alitas no encontradas"}
    alita.orden = alitas.orden
    alita.precio = alitas.precio
    alita.id_cat = alitas.id_cat
    session.add(alita)
    session.commit()
    session.refresh(alita)
    return {"message": "Alitas actualizadas correctamente"}


@router.post("/")
def createAlitas(
    alitas: createAlitas, 
    session: Session = Depends(get_session), 
    _: None = Depends(require_permission("crear_producto"))  # ← Permiso para CREAR
):
    alita = Alita(
        orden=alitas.orden,
        precio=alitas.precio,
        id_cat=alitas.id_cat
    )
    session.add(alita)
    session.commit()
    session.refresh(alita)
    return {"message": "Alitas registradas correctamente"}


@router.delete("/{id_alis}")
def deleteAlitas(
    id_alis: int, 
    session: Session = Depends(get_session), 
    _: None = Depends(require_permission("eliminar_producto"))  # ← Permiso para ELIMINAR
):
    alita = session.get(Alita, id_alis)
    if not alita:
        return {"message": "Alitas no encontradas"}
    session.delete(alita)
    session.commit()
    return {"message": "Alitas eliminadas correctamente"}