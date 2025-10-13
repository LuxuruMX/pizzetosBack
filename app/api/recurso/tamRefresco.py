from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.tamanosRefrescosModel import tamanosRefrescos
from app.schemas.tamanosRefrescosSchema import createTamanosRefrescos, readTamanosRefrescos


router = APIRouter()

@router.get("/", response_model=List[readTamanosRefrescos])
def getTamanosRefrescos(session: Session = Depends(get_session)):
    statement = select(tamanosRefrescos)
    results = session.exec(statement).all()
    return results

@router.get("/{id_tamano}", response_model=readTamanosRefrescos)
def getTamanosRefrescosById(id_tamano: int, session: Session = Depends(get_session)):
    statement = select(tamanosRefrescos).where(tamanosRefrescos.id_tamano == id_tamano)
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=404, detail="Tamaño no encontrado")
    return result

@router.post("/")
def createTamanosRefresco(tam_data: createTamanosRefrescos, session: Session = Depends(get_session)):
    existencia = session.exec(select(tamanosRefrescos).where(tamanosRefrescos.tamano == tam_data.tamano)).first()
    if existencia:
        return {"error": "El tamaño ya existe"}
    new_tamano = tamanosRefrescos(tamano=tam_data.tamano, precio=tam_data.precio)
    session.add(new_tamano)
    session.commit()
    session.refresh(new_tamano)
    return {"message": "Tamaño creado"}

@router.put("/{id_tamano}")
def updateTamanosRefrescos(id_tamano: int, tam_data: createTamanosRefrescos, session: Session = Depends(get_session)):
    existe = session.get(tamanosRefrescos, id_tamano)
    if not existe:
        raise HTTPException(status_code=404, detail="Tamaño no encontrado")
    existe.tamano = tam_data.tamano
    existe.precio = tam_data.precio
    session.add(existe)
    session.commit()
    session.refresh(existe)
    return {"message": "Tamaño actualizado"}

@router.delete("/{id_tamano}")
def deleteTamanosRefrescos(id_tamano: int, session: Session = Depends(get_session)):
    existe = session.get(tamanosRefrescos, id_tamano)
    if not existe:
        raise HTTPException(status_code=404, detail="Tamaño no encontrado")
    session.delete(existe)
    session.commit()
    return {"message": "Tamaño eliminado"}