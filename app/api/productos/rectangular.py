from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.permissions import require_permission, require_any_permission

from app.models.rectangularModel import rectangular 
from app.schemas.rectangularSchema import readRectangularOut, createRectangular

from app.models.categoriaModel import categoria as CategoriasProd
from app.models.especialidadModel import especialidad

router = APIRouter()


@router.get("/", response_model=List[readRectangularOut])
def getRectangular(session: Session = Depends(get_session), _: None = Depends(require_permission("ver_producto"))):
    statement = (
        select(rectangular.id_rec, especialidad.nombre.label("especialidad"),CategoriasProd.descripcion.label("categoria"), rectangular.precio)
        .join(CategoriasProd, rectangular.id_cat == CategoriasProd.id_cat)
        .join(especialidad, rectangular.id_esp == especialidad.id_esp)
    )

    results = session.exec(statement).all()
    return [readRectangularOut(
        id_rec=r.id_rec,
        especialidad=r.especialidad,
        categoria=r.categoria,
        precio=r.precio
    ) for r in results]
    
@router.get("/{id_rec}", response_model=readRectangularOut)
def getRectangularById(id_rec: int, session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_producto", "modificar_producto"))):
    statement = (
        select(rectangular.id_rec, especialidad.nombre.label("especialidad"),CategoriasProd.descripcion.label("categoria"), rectangular.precio)
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
        categoria=result.categoria,
        precio=result.precio
    )
    
@router.put("/{id_rec}")
def updateRectangular(id_rec: int, rectangular_data: createRectangular, session: Session = Depends(get_session), _: None = Depends(require_permission("modificar_producto"))):
    rectangular_item = session.get(rectangular, id_rec)
    if not rectangular_item:
        return {"message": "Rectangular no encontrado"}
    
    rectangular_item.id_esp = rectangular_data.id_esp
    rectangular_item.id_cat = rectangular_data.id_cat
    rectangular_item.precio = rectangular_data.precio
    
    session.add(rectangular_item)
    session.commit()
    session.refresh(rectangular_item)
    return {"message": "Rectangular actualizado correctamente"}

@router.post("/")
def createRectangulares(rectangular_data: createRectangular, session: Session = Depends(get_session), _: None = Depends(require_permission("crear_producto"))):
    new_rectangular = rectangular(
        id_esp=rectangular_data.id_esp,
        id_cat=rectangular_data.id_cat,
        precio=rectangular_data.precio
    )
    session.add(new_rectangular)
    session.commit()
    session.refresh(new_rectangular)
    return {"message": "Rectangular creado correctamente"}

@router.delete("/{id_rec}")
def deleteRectangular(id_rec: int, session: Session = Depends(get_session), _: None = Depends(require_permission("eliminar_producto"))):
    rectangular_item = session.get(rectangular, id_rec)
    if not rectangular_item:
        return {"message": "Rectangular no encontrado"}
    
    session.delete(rectangular_item)
    session.commit()
    return {"message": "Rectangular eliminado correctamente"}