from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.tamanosPizzasModel import tamanosPizzas
from app.schemas.tamanosPizzaSchema import createTamanosPizza, readTamanosPizza


router = APIRouter()

@router.get("/", response_model=List[readTamanosPizza])
def getTamanosPizzas(session: Session = Depends(get_session)):
    statement = select(tamanosPizzas)
    results = session.exec(statement).all()
    return results

@router.get("/{id_tamanop}", response_model=readTamanosPizza)  # Sin ñ en la ruta
def getTamanosPizzasById(id_tamanop: int, session: Session = Depends(get_session)):  # Sin ñ
    statement = select(tamanosPizzas).where(tamanosPizzas.id_tamañop == id_tamanop)  # Con ñ en la columna
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Tamaño no encontrado")
    return result

@router.post("/")
def createTamanosPizzas(tam_data: createTamanosPizza, session: Session = Depends(get_session)):
    existencia = session.exec(select(tamanosPizzas).where(tamanosPizzas.tamano == tam_data.tamano)).first()
    if existencia:
        return {"error": "El tamaño ya existe"}
    new_tamano = tamanosPizzas(tamano=tam_data.tamano, precio=tam_data.precio)
    session.add(new_tamano)
    session.commit()
    session.refresh(new_tamano)
    return {"message": "Tamaño creado"}

@router.put("/{id_tamanop}")
def updateTamanosPizzas(id_tamanop: int, tam_data: createTamanosPizza, session: Session = Depends(get_session)):
    existe = session.get(tamanosPizzas, id_tamanop)
    if not existe:
        raise HTTPException(status_code=404, detail="Tamaño no encontrado")
    existe.tamano = tam_data.tamano
    existe.precio = tam_data.precio
    session.add(existe)
    session.commit()
    session.refresh(existe)
    return {"message": "Tamaño actualizado"}

@router.delete("/{id_tamanop}")
def deleteTamanosPizzas(id_tamanop: int, session: Session = Depends(get_session)):
    existe = session.get(tamanosPizzas, id_tamanop)
    if not existe:
        raise HTTPException(status_code=404, detail="Tamaño no encontrado")
    session.delete(existe)
    session.commit()
    return {"message": "Tamaño eliminado"}