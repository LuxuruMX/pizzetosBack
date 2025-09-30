from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.api.productos import (alitas, 
                               costillas, 
                               especialidad, 
                               hamburguesas, 
                               refrescos, 
                               papas, 
                               mariscos, 
                               magno, 
                               spaguetty)

from app.models.categoriaModel import categoria as CategoriasProd
from app.models.tamanosPizzasModel import tamanosPizzas
from app.models.tamanosRefrescosModel import tamanosRefrescos


router=APIRouter()


@router.get("/categoria", tags=["Categoria"], response_model=List[CategoriasProd])
def getCategoria(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(CategoriasProd)
    results = session.exec(statement).all()
    return results

@router.get("/tamanos-pizza", tags=["Tamaños Pizza"], response_model=List[tamanosPizzas])
def getTamanosPizza(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(tamanosPizzas)
    results = session.exec(statement).all()
    return results

@router.get("/tamanos-refresco", tags=["Tamaños Refresco"], response_model=List[tamanosRefrescos])
def getTamanosRefresco(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(tamanosRefrescos)
    results = session.exec(statement).all()
    return results



router.include_router(alitas.router, prefix="/alitas", tags=["Alitas"])
router.include_router(costillas.router, prefix="/costillas", tags=["Costillas"])
router.include_router(especialidad.router, prefix="/especialidad", tags=["Especialidad"])
router.include_router(hamburguesas.router, prefix="/hamburguesas", tags=["Hamburguesas"])
router.include_router(refrescos.router, prefix="/refrescos", tags=["Refrescos"])
router.include_router(papas.router, prefix="/papas", tags=["Papas"])
router.include_router(mariscos.router, prefix="/mariscos", tags=["Mariscos"])
router.include_router(magno.router, prefix="/magno", tags=["Magno"])
router.include_router(spaguetty.router, prefix="/spaguetty", tags=["Spaguetty"])
