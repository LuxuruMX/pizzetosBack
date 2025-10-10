from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.sucursalModel import Sucursal
from app.schemas.sucursalSchema import readSucursal, createSucursal


router = APIRouter()


@router.get("/", response_model=List[readSucursal])
def getSucursales(session: Session = Depends(get_session)):
    statement = select(Sucursal)
    results = session.exec(statement).all()
    return [readSucursal(
        id_suc=r.id_suc,
        nombre=r.nombre,
        direccion=r.direccion,
        telefono=r.telefono        
    )for r in results]
    
    
@router.get("/{id_suc}")
def getSucursalById(id_suc: int, session: Session = Depends(get_session)):
    statement = (
        select(Sucursal)
        .where(Sucursal.id_suc == id_suc)
        )
    result = session.exec(statement).first()
    if result:
        return readSucursal(
            id_suc=result.id_suc,
            nombre=result.nombre,
            direccion=result.direccion,
            telefono=result.telefono  
        )
    return {"message": "Sucursal no encontrada"}


@router.post("/")
def createSucursales(sucursal: createSucursal, session: Session = Depends(get_session)):
    statement = Sucursal(
        nombre=sucursal.nombre,
        direccion=sucursal.direccion,
        telefono=sucursal.telefono
    )
    session.add(statement)
    session.commit()
    session.refresh(statement)
    return {"message": "Sucursal creada con exito"}


@router.delete("/")
def deleteSucursal(id_suc: int, session: Session = Depends(get_session)):
    statement = session.get(Sucursal, id_suc)
    if not statement:
        return {"Message": "Sucursal no encontrada"}
    session.delete(statement)
    session.commit()
    return {"Message": "Sucursal Eliminada"}



@router.put("/{id_suc}")
def updateSucursal(sucursal: createSucursal, id_suc: int, session: Session = Depends(get_session)):
    statement = session.get(Sucursal, id_suc)
    if not statement:
        return {"Message": "Sucursal no encontrada"}
    statement.nombre=sucursal.nombre
    statement.direccion=sucursal.direccion
    statement.telefono=statement.telefono
    session.add(statement)
    session.commit()
    session.refresh(statement)
    return {"Message": "Sucursal actualizada correctamente"}