from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.permissions import require_permission, require_any_permission

from app.models.barraModel import barra
from app.schemas.barraSchema import readBarraOut, createBarra

from app.models.categoriaModel import categoria as CategoriasProd
from app.models.especialidadModel import especialidad

router = APIRouter()

@router.get("/", response_model=List[readBarraOut])
def getBarra(session: Session = Depends(get_session), _: None = Depends(require_permission("ver_producto"))):
    statement = (
        select(barra.id_barr, especialidad.nombre.label("especialidad"), CategoriasProd.descripcion.label("categoria"), barra.precio)
        .join(especialidad, barra.id_especialidad == especialidad.id_esp)
        .join(CategoriasProd, barra.id_cat == CategoriasProd.id_cat)
    )

    results = session.exec(statement).all()
    return [readBarraOut(
        id_barr=r.id_barr,
        especialidad=r.especialidad,
        categoria=r.categoria,
        precio=r.precio
    ) for r in results]
    
@router.get("/{id_barr}", response_model=readBarraOut)
def getBarraById(id_barr: int, session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_producto", "modificar_producto"))):
    statement = (
        select(barra.id_barr, especialidad.nombre.label("especialidad"), CategoriasProd.descripcion.label("categoria"), barra.precio)
        .join(especialidad, barra.id_especialidad == especialidad.id_esp)
        .join(CategoriasProd, barra.id_cat == CategoriasProd.id_cat)
        .where(barra.id_barr == id_barr)
    )

    result = session.exec(statement).first()
    if result:
        return readBarraOut(
            id_barr=result.id_barr,
            especialidad=result.especialidad,
            categoria=result.categoria,
            precio=result.precio
        )
    return {"message": "Producto de barra no encontrado"}

@router.put("/{id_barr}")
def updateBarra(id_barr: int, barra_data: createBarra, session: Session = Depends(get_session), _: None = Depends(require_permission("modificar_producto"))):
    barra_item = session.get(barra, id_barr)
    if not barra_item:
        return {"message": "Producto de barra no encontrado"}
    barra_item.id_especialidad = barra_data.id_especialidad
    barra_item.id_cat = barra_data.id_cat
    barra_item.precio = barra_data.precio
    session.add(barra_item)
    session.commit()
    session.refresh(barra_item)
    return {"message": "Producto de barra actualizado correctamente"}

@router.post("/")
def createBarraItem(barra_data: createBarra, session: Session = Depends(get_session), _: None = Depends(require_permission("crear_producto"))):
    new_barra = barra(
        id_especialidad=barra_data.id_especialidad,
        id_cat=barra_data.id_cat,
        precio=barra_data.precio
    )
    session.add(new_barra)
    session.commit()
    session.refresh(new_barra)

    return {"message": "Producto de barra creado correctamente"}
    
@router.delete("/{id_barr}")
def deleteBarra(id_barr: int, session: Session = Depends(get_session), _: None = Depends(require_permission("eliminar_producto"))):
    barra_item = session.get(barra, id_barr)
    if not barra_item:
        return {"message": "Producto de barra no encontrado"}
    session.delete(barra_item)
    session.commit()
    return {"message": "Producto de barra eliminado correctamente"}