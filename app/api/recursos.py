from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from argon2 import PasswordHasher
from app.core.dependency import verify_token

from app.models.sucursalModel import Sucursal
from app.schemas.sucursalSchema import readSucursal

from app.api.recurso import (cargos)

router = APIRouter()
ph = PasswordHasher()



@router.get("/sucursales", response_model=List[readSucursal])
def getSucursal(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = select(Sucursal)
    results = session.exec(statement).all()
    return results


router.include_router(cargos.router, prefix="/cargos", tags=["cargos"])