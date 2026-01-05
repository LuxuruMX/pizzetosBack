from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from app.db.session import get_session
from argon2 import PasswordHasher
from datetime import time, datetime
from fastapi import Query

from app.models.gastosModel import Gastos
from app.schemas.gastosSchema import readGastos, createGastos
from app.models.sucursalModel import Sucursal
from app.core.permissions import require_permission, require_any_permission


router = APIRouter()
ph = PasswordHasher()


@router.get("/{id_caja}/caja", response_model=List[readGastos])
async def getGastosPorCaja(
    id_caja: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("ver_recurso"))
):
    statement = (
        select(Gastos.id_gastos, Gastos.id_suc, Gastos.descripcion, Gastos.precio, Gastos.fecha, Sucursal.nombre.label("sucursal"), Gastos.evaluado)
        .join(Sucursal, Gastos.id_suc == Sucursal.id_suc)
        .where(Gastos.id_caja == id_caja)
        .order_by(Gastos.id_gastos)
    )
    
    results = session.exec(statement).all()
    return results



@router.get("/", response_model=List[readGastos])
async def getGastos(
    session: Session = Depends(get_session),
    id_suc: int = Query(..., description="ID de la sucursal. 1 para ver todas, 2, 3, etc para ver solo esa sucursal"),
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio para filtrar (formato: YYYY-MM-DD o ISO 8601)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin para filtrar (formato: YYYY-MM-DD o ISO 8601)"),
    _: None = Depends(require_permission("ver_recurso"))
):
    statement = (
        select(Gastos.id_gastos, Gastos.id_suc, Gastos.descripcion, Gastos.precio, Gastos.fecha, Sucursal.nombre.label("sucursal"), Gastos.evaluado)
        .join(Sucursal, Gastos.id_suc == Sucursal.id_suc)
        .order_by(Gastos.id_gastos)
    )

    # Filtrar por sucursal: si id_suc == 1 -> todas las sucursales, si !=1 -> solo esa sucursal
    if id_suc != 1:
        statement = statement.where(Gastos.id_suc == id_suc)

    # Parsear fechas si se proporcionan
    dt_inicio = None
    dt_fin = None

    if fecha_inicio:
        try:
            dt_inicio = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
        except ValueError:
            try:
                dt_fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                dt_inicio = datetime.combine(dt_fecha_inicio, time.min)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha_inicio inválido. Use YYYY-MM-DD o ISO 8601.")

    if fecha_fin:
        try:
            dt_fin = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
        except ValueError:
            try:
                dt_fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                dt_fin = datetime.combine(dt_fecha_fin, time.max)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha_fin inválido. Use YYYY-MM-DD o ISO 8601.")

    if dt_inicio:
        statement = statement.where(Gastos.fecha >= dt_inicio)
    if dt_fin:
        statement = statement.where(Gastos.fecha <= dt_fin)

    results = session.exec(statement).all()
    return results

@router.post("/")
async def create_gasto(gasto: createGastos, session: Session = Depends(get_session), _: None = Depends(require_permission("crear_recurso"))):
    new_gasto = Gastos(
        id_suc=gasto.id_suc,
        descripcion=gasto.descripcion,
        precio=gasto.precio,
        id_caja=gasto.id_caja
    )
    session.add(new_gasto)
    session.commit()
    session.refresh(new_gasto)
    return {"message":"Gasto creado"}

@router.get("/{id_gastos}", response_model=readGastos)
async def getGastoById(id_gastos: int, session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_recurso", "modificar_recurso"))):
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
async def deleteGastoById(id_gastos: int, session: Session = Depends(get_session), _: None = Depends(require_permission("eliminar_recurso"))):
    statement = select(Gastos).where(Gastos.id_gastos == id_gastos)
    result = session.exec(statement).first()
    if result:
        session.delete(result)
        session.commit()
        return {"message":"Gasto eliminado"}
    return {"message":"No se encontro el gasto"}

@router.put("/{id_gastos}")
async def updateGasto(id_gastos: int, gasto: createGastos, session: Session = Depends(get_session), _: None = Depends(require_permission("modificar_recurso"))):
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


