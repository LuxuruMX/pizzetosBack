from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.magnoModel import magno
from app.schemas.magnoSchema import readMagnoOut, createMagno

from app.models.refrescosModel import refrescos
from app.models.especialidadModel import especialidad

router = APIRouter()

@router.get("/", response_model=List[readMagnoOut])
def getMagno(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(magno.id_magno, especialidad.nombre.label("especialidad"), refrescos.nombre.label("refresco"), magno.precio)
        .join(especialidad, magno.id_especialidad == especialidad.id_esp)
        .join(refrescos, magno.id_refresco == refrescos.id_refresco)
    )

    results = session.exec(statement).all()
    return [readMagnoOut(
        id_magno=r.id_magno,
        especialidad=r.especialidad,
        refresco=r.refresco,
        precio=r.precio
    ) for r in results]
    
@router.get("/{id_magno}", response_model=readMagnoOut)
def getMagnoById(id_magno: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(magno.id_magno, especialidad.nombre.label("especialidad"), refrescos.nombre.label("refresco"), magno.precio)
        .join(especialidad, magno.id_especialidad == especialidad.id_esp)
        .join(refrescos, magno.id_refresco == refrescos.id_refresco)
        .where(magno.id_magno == id_magno)
    )

    result = session.exec(statement).first()
    if result:
        return readMagnoOut(
            id_magno=result.id_magno,
            especialidad=result.especialidad,
            refresco=result.refresco,
            precio=result.precio
        )
    return {"message": "Magno no encontrado"}

@router.put("/{id_magno}")
def updateMagno(id_magno: int, mag: createMagno, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    magno_item = session.get(magno, id_magno)
    if not magno_item:
        return {"message": "Magno no encontrado"}
    magno_item.id_especialidad = mag.id_especialidad
    magno_item.id_refresco = mag.id_refresco
    magno_item.precio = mag.precio
    session.add(magno_item)
    session.commit()
    session.refresh(magno_item)
    return {"message": "Magno actualizado correctamente"}

@router.post("/")
def createMagnos(mag: createMagno, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    magno_item = magno(
        id_especialidad= mag.id_especialidad,
        id_refresco= mag.id_refresco,
        precio= mag.precio
    )
    session.add(magno_item)
    session.commit()
    session.refresh(magno_item)
    return {"message" : "Magno registrado correctamente"}

@router.delete("/{id_magno}")
def deleteMagno(id_magno: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    magno_item = session.get(magno, id_magno)
    if not magno_item:
        return {"message": "Magno no encontrado"}
    session.delete(magno_item)
    session.commit()
    return {"message": "Magno eliminado correctamente"}