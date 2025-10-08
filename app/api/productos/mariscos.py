from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.mariscosModel import mariscos
from app.schemas.mariscosSchema import readMariscosOut, createMariscos

from app.models.categoriaModel import categoria as CategoriasProd
from app.models.tamanosPizzasModel import tamanosPizzas

router = APIRouter()

@router.get("/",response_model=List[readMariscosOut])
def get_mariscos(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(
            mariscos.id_maris,
            mariscos.nombre,
            mariscos.descripcion,
            tamanosPizzas.tamano.label("tamaño"),
            CategoriasProd.descripcion.label("categoria")
        )
        .join(tamanosPizzas, mariscos.id_tamañop == tamanosPizzas.id_tamañop)
        .join(CategoriasProd, mariscos.id_cat == CategoriasProd.id_cat)
    )
    results = session.exec(statement).all()
    return [readMariscosOut(
        id_maris=r.id_maris,
        nombre=r.nombre,
        descripcion=r.descripcion,
        tamaño=r.tamaño,
        categoria=r.categoria
    ) for r in results]

@router.get("/{id_maris}", response_model=readMariscosOut)
def get_mariscos_by_id(id_maris: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(
            mariscos.id_maris,
            mariscos.nombre,
            mariscos.descripcion,
            tamanosPizzas.tamano.label("tamaño"),
            CategoriasProd.descripcion.label("categoria")
        )
        .join(tamanosPizzas, mariscos.id_tamañop == tamanosPizzas.id_tamañop)
        .join(CategoriasProd, mariscos.id_cat == CategoriasProd.id_cat)
        .where(mariscos.id_maris == id_maris)
    )
    result = session.exec(statement).first()
    if result:
        return readMariscosOut(
            id_maris=result.id_maris,
            nombre=result.nombre,
            descripcion=result.descripcion,
            tamaño=result.tamaño,
            categoria=result.categoria
        )
    return {"message": "Mariscos no encontrados"}

@router.put("/{id_maris}")
def update_mariscos(id_maris: int, mariscos_data: createMariscos, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    marisco = session.get(mariscos, id_maris)
    if not marisco:
        return {"message": "Mariscos no encontrados"}
    marisco.nombre = mariscos_data.nombre
    marisco.descripcion = mariscos_data.descripcion
    marisco.id_tamañop = mariscos_data.id_tamañop
    marisco.id_cat = mariscos_data.id_cat
    session.add(marisco)
    session.commit()
    session.refresh(marisco)
    return {"message": "Mariscos actualizados correctamente"}

@router.post("/")
def create_mariscos(mariscos_data: createMariscos, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    marisco = mariscos(
        nombre=mariscos_data.nombre,
        descripcion=mariscos_data.descripcion,
        id_tamañop=mariscos_data.id_tamañop,
        id_cat=mariscos_data.id_cat
    )
    session.add(marisco)
    session.commit()
    session.refresh(marisco)
    return {"message": "Mariscos registrados correctamente"}

@router.delete("/{id_maris}")
def delete_mariscos(id_maris: int, session: Session = Depends(get_session), token: str = Depends(verify_token)):
    marisco = session.get(mariscos, id_maris)
    if not marisco:
        return {"message": "Mariscos no encontrados"}
    session.delete(marisco)
    session.commit()
    return {"message": "Mariscos eliminados correctamente"}