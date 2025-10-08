from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.papasModel import papas
from app.schemas.papasSchema import readPapasOut, createPapas

from app.models.categoriaModel import categoria as CategoriasProd

router = APIRouter()

@router.get("/", response_model=List[readPapasOut])
def getPapas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(papas.id_papa, papas.orden, papas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, papas.id_cat == CategoriasProd.id_cat)
    )

    results = session.exec(statement).all()
    return [readPapasOut(
        id_papa=r.id_papa,
        orden=r.orden,
        precio=r.precio,
        categoria=r.categoria
    ) for r in results]
    
@router.get("/{id_papa}", response_model=readPapasOut)
def getPapasById(id_papa: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(papas.id_papa, papas.orden, papas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, papas.id_cat == CategoriasProd.id_cat)
        .where(papas.id_papa == id_papa)
    )

    result = session.exec(statement).first()
    if result:
        return readPapasOut(
            id_papa=result.id_papa,
            orden=result.orden,
            precio=result.precio,
            categoria=result.categoria
        )
    return {"message": "Papas no encontradas"}

@router.put("/{id_papa}")
def updatePapas(id_papa: int, papas_data: createPapas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    papa = session.get(papas, id_papa)
    if not papa:
        return {"message": "Papas no encontradas"}
    papa.orden = papas_data.orden
    papa.precio = papas_data.precio
    papa.id_cat = papas_data.id_cat
    session.add(papa)
    session.commit()
    session.refresh(papa)
    return {"message": "Papas actualizadas correctamente"}

@router.post("/")
def createPapasEndpoint(papas_data: createPapas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    new_papa = papas(
        orden=papas_data.orden,
        precio=papas_data.precio,
        id_cat=papas_data.id_cat
    )
    session.add(new_papa)
    session.commit()
    session.refresh(new_papa)
    return {"message": "Papas creadas correctamente"}

@router.delete("/{id_papa}")
def deletePapas(id_papa: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    papa = session.get(papas, id_papa)
    if not papa:
        return {"message": "Papas no encontradas"}
    session.delete(papa)
    session.commit()
    return {"message": "Papas eliminadas correctamente"}