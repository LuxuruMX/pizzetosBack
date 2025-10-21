from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from argon2 import PasswordHasher
from app.core.permissions import require_permission, require_any_permission

from app.models.gastosModel import Gastos
from app.schemas.gastosSchema import readGastos, createGastos

from app.models.sucursalModel import Sucursal


router = APIRouter()
ph = PasswordHasher()


@router.get("/", response_model=List[readGastos])
def getGastos(session: Session = Depends(get_session), _: None = Depends(require_permission("ver_recurso"))):
    statement = (
        select(Gastos.id_gastos, Gastos.id_suc, Gastos.descripcion, Gastos.precio, Gastos.fecha, Sucursal.nombre.label("sucursal"), Gastos.evaluado)
        .join(Sucursal, Gastos.id_suc == Sucursal.id_suc)
        .order_by(Gastos.id_gastos)
    )
    results = session.exec(statement).all()
    return results

@router.post("/")
def create_gasto(gasto: createGastos, session: Session = Depends(get_session), _: None = Depends(require_permission("crear_recurso"))):
    new_gasto = Gastos(**gasto.model_dump())
    session.add(new_gasto)
    session.commit()
    session.refresh(new_gasto)
    return {"message":"Gasto creado"}

@router.get("/{id_gastos}", response_model=readGastos)
def getGastoById(id_gastos: int, session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_recurso", "modificar_recurso"))):
    statement = (
        select(Gastos.id_gastos, Gastos.id_suc, Gastos.descripcion, Gastos.precio, Gastos.fecha, Sucursal.nombre.label("sucursal"), Gastos.evaluado)
        .join(Sucursal, Gastos.id_suc == Sucursal.id_suc)
        .where(Gastos.id_gastos == id_gastos)
    )
    
    result = session.exec(statement).first()
    if result:
        return readGastos(
            id_gastos=result.id_gastos,
            id_suc=result.id_suc,
            descripcion=result.descripcion,
            precio=result.precio,
            fecha=result.fecha,
            sucursal=result.sucursal,
            evaluado=result.evaluado
        )
    return {"message":"No se encontro el gasto"}

@router.delete("/{id_gastos}")
def deleteGastoById(id_gastos: int, session: Session = Depends(get_session), _: None = Depends(require_permission("eliminar_recurso"))):
    statement = select(Gastos).where(Gastos.id_gastos == id_gastos)
    result = session.exec(statement).first()
    if result:
        session.delete(result)
        session.commit()
        return {"message":"Gasto eliminado"}
    return {"message":"No se encontro el gasto"}

@router.put("/{id_gastos}")
def updateGasto(id_gastos: int, gasto: createGastos, session: Session = Depends(get_session), _: None = Depends(require_permission("modificar_recurso"))):
    statement = select(Gastos).where(Gastos.id_gastos == id_gastos)
    result = session.exec(statement).first()
    if result:
        result.id_suc = gasto.id_suc
        result.descripcion = gasto.descripcion
        result.precio = gasto.precio
        session.add(result)
        session.commit()
        session.refresh(result)
        return {"message":"Gasto actualizado"}
    return {"message":"No se encontro el gasto"}