from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.rectangularModel import rectangular 
from app.schemas.rectangularSchema import readRectangularOut, createRectangular

from app.models.categoriaModel import categoria as CategoriasProd
from app.models.especialidadModel import especialidad

router = APIRouter()


@router.get("/", response_model=List[readRectangularOut])
def getRectangular(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(rectangular.id_rec, especialidad.nombre.label("especialidad"),CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, rectangular.id_cat == CategoriasProd.id_cat)
        .join(especialidad, rectangular.id_esp == especialidad.id_esp)
    )

    results = session.exec(statement).all()
    return [readRectangularOut(
        id_rec=r.id_rec,
        especialidad=r.especialidad,
        categoria=r.categoria
    ) for r in results]
    
@router.get("/{id_rec}", response_model=readRectangularOut)
def getRectangularById(id_rec: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(rectangular.id_rec, especialidad.nombre.label("especialidad"),CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, rectangular.id_cat == CategoriasProd.id_cat)
        .join(especialidad, rectangular.id_esp == especialidad.id_esp)
        .where(rectangular.id_rec == id_rec)
    )

    result = session.exec(statement).first()
    if not result:
        return None
    return readRectangularOut(
        id_rec=result.id_rec,
        especialidad=result.especialidad,
        categoria=result.categoria
    )
    
@router.put("/editar-rectangular/{id_rec}")
def updateRectangular(id_rec: int, rectangular_data: createRectangular, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    rectangular_item = session.get(rectangular, id_rec)
    if not rectangular_item:
        return {"message": "Rectangular no encontrado"}
    
    rectangular_item.id_esp = rectangular_data.id_esp
    rectangular_item.id_cat = rectangular_data.id_cat
    
    session.add(rectangular_item)
    session.commit()
    session.refresh(rectangular_item)
    return {"message": "Rectangular actualizado correctamente"}

@router.post("/crear-rectangular")
def createRectangular(rectangular_data: createRectangular, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    new_rectangular = rectangular(
        id_esp=rectangular_data.id_esp,
        id_cat=rectangular_data.id_cat
    )
    session.add(new_rectangular)
    session.commit()
    session.refresh(new_rectangular)
    return {"message": "Rectangular creado correctamente"}

@router.delete("/eliminar-rectangular/{id_rec}")
def deleteRectangular(id_rec: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    rectangular_item = session.get(rectangular, id_rec)
    if not rectangular_item:
        return {"message": "Rectangular no encontrado"}
    
    session.delete(rectangular_item)
    session.commit()
    return {"message": "Rectangular eliminado correctamente"}