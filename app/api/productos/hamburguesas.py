from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.permissions import require_permission, require_any_permission

from app.models.hamburguesasModel import hamburguesas
from app.schemas.hamburguesasSchema import createHamburguesas, readHamburguesasOut

from app.models.categoriaModel import categoria as CategoriasProd

router = APIRouter()

@router.get("/", response_model=List[readHamburguesasOut])
def getHamburguesas(session: Session = Depends(get_session), _: None = Depends(require_permission("ver_producto"))):
    statement=(
        select(hamburguesas.id_hamb, hamburguesas.paquete, hamburguesas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, hamburguesas.id_cat == CategoriasProd.id_cat)
    )
    results = session.exec(statement).all()
    return [readHamburguesasOut(
        id_hamb=r.id_hamb,
        paquete=r.paquete,
        precio=r.precio,
        categoria=r.categoria
    ) for r in results]

@router.get("/{id_hamb}", response_model=readHamburguesasOut)
def getHamburguesaById(id_hamb: int, session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_producto", "modificar_producto"))):
    statement = (
        select(hamburguesas.id_hamb, hamburguesas.paquete, hamburguesas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, hamburguesas.id_cat == CategoriasProd.id_cat)
        .where(hamburguesas.id_hamb == id_hamb)
    )

    result = session.exec(statement).first()
    if result:
        return readHamburguesasOut(
            id_hamb=result.id_hamb,
            paquete=result.paquete,
            precio=result.precio,
            categoria=result.categoria
        )
    return {"message": "Hamburguesa no encontrada"}

@router.put("/{id_hamb}")
def updateHamburguesa(id_hamb: int, hamburguesa_data: createHamburguesas, session: Session = Depends(get_session), _: None = Depends(require_permission("modificar_producto"))):
    hamburguesa_item = session.get(hamburguesas, id_hamb)
    if not hamburguesa_item:
        return {"message": "Hamburguesa no encontrada"}
    
    hamburguesa_item.paquete = hamburguesa_data.paquete
    hamburguesa_item.precio = hamburguesa_data.precio
    hamburguesa_item.id_cat = hamburguesa_data.id_cat
    
    session.add(hamburguesa_item)
    session.commit()
    session.refresh(hamburguesa_item)
    
    return {"message": "Hamburguesa actualizada correctamente"}

@router.post("/")
def createHamburguesa(hamburguesa_data: createHamburguesas, session: Session = Depends(get_session), _: None = Depends(require_permission("crear_producto"))):
    nueva_hamburguesa = hamburguesas(
        paquete= hamburguesa_data.paquete,
        precio= hamburguesa_data.precio,
        id_cat= hamburguesa_data.id_cat
    )
    session.add(nueva_hamburguesa)
    session.commit()
    session.refresh(nueva_hamburguesa)
    return {"message": "Hamburguesa registrada correctamente"}

@router.delete("/{id_hamb}")
def deleteHamburguesa(id_hamb: int, session: Session = Depends(get_session), _: None = Depends(require_permission("eliminar_producto"))):
    
    hamburguesa_item = session.get(hamburguesas, id_hamb)
    if not hamburguesa_item:
        return {"message": "Hamburguesa no encontrada"}
    session.delete(hamburguesa_item)
    session.commit()
    return {"message": "Hamburguesa eliminada correctamente"}

