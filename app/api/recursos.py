from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from argon2 import PasswordHasher
from app.core.dependency import verify_token

from app.models.cargoModel import Cargos
from app.schemas.cargoSchema import readCargo

from app.models.sucursalModel import Sucursal
from app.schemas.sucursalSchema import readSucursal


router = APIRouter()
ph = PasswordHasher()


@router.get("/cargos", response_model=List[readCargo])
def getCargo(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = select(Cargos)
    results = session.exec(statement).all()
    return results





@router.get("/sucursales", response_model=List[readSucursal])
def getSucursal(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = select(Sucursal)
    results = session.exec(statement).all()
    return results