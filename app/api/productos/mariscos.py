from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.mariscosModel import mariscos
from app.schemas.alitasSchema import readAlitasOut, createAlitas

from app.models.categoriaModel import categoria as CategoriasProd
from app.models.tamanosPizzasModel import tamanosPizzas

router = APIRouter()

@router.get("/", response_model=List[readAlitasOut])
def getMariscos(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(mariscos.id_maris, mariscos.nombre, mariscos.descripcion, CategoriasProd.descripcion.label("categoria"), tamanosPizzas.descripcion.label("tamaño"))
        .join(CategoriasProd, mariscos.id_cat == CategoriasProd.id_cat)
        .join(tamanosPizzas, mariscos.id_tamañop == tamanosPizzas.id_tamañop)
    )

    results = session.exec(statement).all()
    return [readAlitasOut(
        id_alis=r.id_maris,
        orden=r.nombre,
        precio=r.descripcion,
        categoria=r.categoria + " - " + r.tamaño
    ) for r in results]
    
@router.get("/{id_maris}", response_model=readAlitasOut)
def getMariscosById(id_maris: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(mariscos.id_maris, mariscos.nombre, mariscos.descripcion, CategoriasProd.descripcion.label("categoria"), tamanosPizzas.descripcion.label("tamaño"))
        .join(CategoriasProd, mariscos.id_cat == CategoriasProd.id_cat)
        .join(tamanosPizzas, mariscos.id_tamañop == tamanosPizzas.id_tamañop)
        .where(mariscos.id_maris == id_maris)
    )

    result = session.exec(statement).first()
    if result:
        return readAlitasOut(
            id_alis=result.id_maris,
            orden=result.nombre,
            precio=result.descripcion,
            categoria=result.categoria + " - " + result.tamaño
        )
    return {"message": "Mariscos no encontrados"}

@router.put("/actualizar-mariscos/{id_maris}")
def updateMariscos(id_maris: int, mariscos: createAlitas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    maris = session.get(mariscos, id_maris)
    if not maris:
        return {"message": "Mariscos no encontrados"}
    maris.nombre = mariscos.orden
    maris.descripcion = mariscos.precio
    maris.id_cat = mariscos.id_cat
    session.add(maris)
    session.commit()
    session.refresh(maris)
    return {"message": "Mariscos actualizados correctamente"}

@router.post("/crear-mariscos")
def createMariscos(maris: createAlitas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    new_maris = mariscos(
        nombre=maris.orden,
        descripcion=maris.precio,
        id_cat=maris.id_cat,
        id_tamañop=maris.id_tamañop
    )
    session.add(new_maris)
    session.commit()
    session.refresh(new_maris)
    return {"message": "Mariscos creados correctamente", "id_maris": new_maris.id_maris}

@router.delete("/eliminar-mariscos/{id_maris}")
def deleteMariscos(id_maris: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    maris = session.get(mariscos, id_maris)
    if not maris:
        return {"message": "Mariscos no encontrados"}
    session.delete(maris)
    session.commit()
    return {"message": "Mariscos eliminados correctamente"}