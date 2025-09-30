from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.alitasModel import alitas as Alita
from app.schemas.alitasSchema import readAlitasOut, createAlitas

from app.models.categoriaModel import categoria as CategoriasProd

router = APIRouter()

@router.get("/", response_model=List[readAlitasOut])
def getAlitas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
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
def getAlitasById(id_alis: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
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
    
    
@router.put("/actualizar-alitas/{id_alis}")
def updateAlitas(id_alis: int, alitas: createAlitas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
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


@router.post("/crear-alitas")
def createAlitas(alitas: createAlitas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    alita=Alita(
        orden= alitas.orden,
        precio=alitas.precio,
        id_cat=alitas.id_cat
    )
    session.add(alita)
    session.commit()
    session.refresh(alita)
    return {"message" : "Alitas registradas correctamente"}

@router.delete("/eliminar-alitas/{id_alis}")
def deleteAlitas(id_alis: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    alita = session.get(Alita, id_alis)
    if not alita:
        return {"message": "Alitas no encontradas"}
    session.delete(alita)
    session.commit()
    return {"message": "Alitas eliminadas correctamente"}