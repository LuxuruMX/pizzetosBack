from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.costillasModel import costillas
from app.schemas.costillasSchema import readCostillasOut, createCostillas

from app.models.categoriaModel import categoria as CategoriasProd

router = APIRouter()

@router.get("/", response_model=List[readCostillasOut])
def getCostillas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(costillas.id_cos, costillas.orden, costillas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, costillas.id_cat == CategoriasProd.id_cat)
    )

    results = session.exec(statement).all()
    return [readCostillasOut(
        id_cos=r.id_cos,
        orden=r.orden,
        precio=r.precio,
        categoria=r.categoria
    ) for r in results]
    

@router.get("/{id_cos}", response_model=readCostillasOut)
def getCostillasById(id_cos: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(costillas.id_cos, costillas.orden, costillas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, costillas.id_cat == CategoriasProd.id_cat)
        .where(costillas.id_cos == id_cos)
    )

    result = session.exec(statement).first()
    if result:
        return readCostillasOut(
            id_cos=result.id_cos,
            orden=result.orden,
            precio=result.precio,
            categoria=result.categoria
        )
    return {"message": "Costillas no encontradas"}



@router.put("/{id_cos}")
def updateCostillas(id_cos: int, costilla_data: createCostillas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    costilla = session.get(costillas, id_cos)
    if not costilla:
        return {"message": "Costillas no encontradas"}
    
    costilla.orden = costilla_data.orden
    costilla.precio = costilla_data.precio
    costilla.id_cat = costilla_data.id_cat
    
    session.add(costilla)
    session.commit()
    session.refresh(costilla)
    
    return {"message": "Costillas actualizadas correctamente"}


@router.post("/")
def createCostilla(costilla: createCostillas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    cost=costillas(
        orden= costilla.orden,
        precio= costilla.precio,
        id_cat= costilla.id_cat
    )
    session.add(cost)
    session.commit()
    session.refresh(cost)
    return {"message": "Costilla registrada orrectamente"}


@router.delete("/{id_cos}")
def deleteCostillas(id_cos: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    costilla = session.get(costillas, id_cos)
    if not costilla:
        return {"message": "Costillas no encontradas"}
    session.delete(costilla)
    session.commit()
    return {"message": "Costillas eliminadas correctamente"}
