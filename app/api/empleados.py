from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.empleadoModel import Empleados
from app.schemas.empleadoSchema import readEmpleado, createEmpleado
from argon2 import PasswordHasher


router = APIRouter()
ph = PasswordHasher()

@router.get("/", response_model=List[readEmpleado])
def get_empleados(session: Session = Depends(get_session)):
    statement = select(Empleados)
    results = session.exec(statement).all()
    return results


@router.post("/agregar")
def addEmpleado(empleado: createEmpleado, session: Session = Depends(get_session)):
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