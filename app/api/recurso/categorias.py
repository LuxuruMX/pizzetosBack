from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.categoriaModel import categoria
from app.schemas.categoriaSchema import readCategoria, createCategoria


router = APIRouter()


@router.get("/", response_model=List[readCategoria])
def getCategorias(session: Session = Depends(get_session)):
    statement = select(categoria)
    results = session.exec(statement).all()
    return results

@router.get("/{id_cat}", response_model=readCategoria)
def getCategoriasById(id_cat: int, session: Session = Depends(get_session)):
    statement = select(categoria).where(categoria.id_cat == id_cat)
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return result

@router.post("/")
def createCategorias(cat_data: createCategoria, session: Session = Depends(get_session)):
    existencia = session.exec(select(categoria).where(categoria.descripcion == cat_data.descripcion)).first()
    if existencia:
        return {"error": "La categoria ya existe"}
    new_categoria = categoria(descripcion=cat_data.descripcion)
    session.add(new_categoria)
    session.commit()
    session.refresh(new_categoria)
    return {"message": "Categoría creada"}

@router.put("/{id_cat}")
def updateCategorias(id_cat: int, cat_data: createCategoria, session: Session = Depends(get_session)):
    existe = session.get(categoria, id_cat)
    if not existe:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    existe.descripcion = cat_data.descripcion
    session.add(existe)
    session.commit()
    session.refresh(existe)
    return {"message": "Categoría actualizada"}

@router.delete("/{id_cat}")
def deleteCategorias(id_cat: int, session: Session = Depends(get_session)):
    existe = session.get(categoria, id_cat)
    if not existe:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    session.delete(existe)
    session.commit()
    return {"message": "Categoría eliminada"}