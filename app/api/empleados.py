from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List, Optional
from app.db.session import get_session
from app.models.empleadoModel import Empleados
from app.schemas.empleadoSchema import readEmpleadoNoPass, createEmpleado
from argon2 import PasswordHasher
from app.core.dependency import verify_token


router = APIRouter()
ph = PasswordHasher()

@router.get("/", response_model=List[readEmpleadoNoPass])
def get_empleados(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = select(Empleados)
    results = session.exec(statement).all()
    return results

@router.get("/sucursal", response_model=List[readEmpleadoNoPass])
def get_empleadosSucursal(id_suc: Optional[int] = None, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = select(Empleados)
    if id_suc is not None:
        statement = statement.where(Empleados.id_suc == id_suc)
    results = session.exec(statement).all()
    return results


@router.post("/agregar")
def addEmpleado(empleado: createEmpleado, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    hashed_password = ph.hash(empleado.password)
    db_empleado = Empleados(
        nombre=empleado.nombre,
        direccion=empleado.direccion,
        telefono=empleado.telefono,
        id_ca=empleado.id_ca,
        id_suc=empleado.id_suc,
        nickName=empleado.nickName,
        password=hashed_password
    )
    session.add(db_empleado)
    session.commit()
    session.refresh(db_empleado)
    return {"message" : "usuario registrado"}