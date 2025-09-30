from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.api.productos import alitas, costillas, especialidad, hamburguesas, refrescos

from app.models.categoriaModel import categoria as CategoriasProd


router=APIRouter()


@router.get("/categoria", tags=["Categoria"])
def getCategoria(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(CategoriasProd)
    results = session.exec(statement).all()
    return results



router.include_router(alitas.router, prefix="/alitas", tags=["Alitas"])
router.include_router(costillas.router, prefix="/costillas", tags=["Costillas"])
router.include_router(especialidad.router, prefix="/especialidad", tags=["Especialidad"])
router.include_router(hamburguesas.router, prefix="/hamburguesas", tags=["Hamburguesas"])
router.include_router(refrescos.router, prefix="/refrescos", tags=["Refrescos"])

