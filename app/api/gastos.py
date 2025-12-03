from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from argon2 import PasswordHasher
from datetime import time
from app.core.permissions import require_permission, require_any_permission

from app.models.gastosModel import Gastos
from app.schemas.gastosSchema import readGastos, createGastos

from app.models.sucursalModel import Sucursal


router = APIRouter()
ph = PasswordHasher()


from datetime import datetime
from typing import Optional
from fastapi import Query

@router.get("/", response_model=List[readGastos])
async def getGastos(
    session: Session = Depends(get_session),
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio para filtrar (formato: YYYY-MM-DD o ISO 8601)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin para filtrar (formato: YYYY-MM-DD o ISO 8601)"),
    _: None = Depends(require_permission("ver_recurso"))
):
    statement = (
        select(Gastos.id_gastos, Gastos.id_suc, Gastos.descripcion, Gastos.precio, Gastos.fecha, Sucursal.nombre.label("sucursal"), Gastos.evaluado)
        .join(Sucursal, Gastos.id_suc == Sucursal.id_suc)
        .order_by(Gastos.id_gastos)
    )

    # Parsear fechas si se proporcionan
    dt_inicio = None
    dt_fin = None

    if fecha_inicio:
        # Intentar parsear como datetime ISO o como fecha simple
        try:
            dt_inicio = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
        except ValueError:
            try:
                dt_fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                dt_inicio = datetime.combine(dt_fecha_inicio, time.min)  # 00:00:00
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha_inicio inválido. Use YYYY-MM-DD o ISO 8601.")

    if fecha_fin:
        try:
            dt_fin = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
        except ValueError:
            try:
                dt_fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                dt_fin = datetime.combine(dt_fecha_fin, time.max)  # 23:59:59.999999
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha_fin inválido. Use YYYY-MM-DD o ISO 8601.")

    # Aplicar filtro de fechas si se han parseado correctamente
    if dt_inicio:
        statement = statement.where(Gastos.fecha >= dt_inicio)
    if dt_fin:
        statement = statement.where(Gastos.fecha <= dt_fin)

    results = session.exec(statement).all()
    return results

@router.post("/")
async def create_gasto(gasto: createGastos, session: Session = Depends(get_session), _: None = Depends(require_permission("crear_recurso"))):
    new_gasto = Gastos(**gasto.model_dump())
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