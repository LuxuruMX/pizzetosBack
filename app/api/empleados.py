from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.empleadoModel import Empleados
from app.schemas.empleadoSchema import readEmpleado

router = APIRouter()

@router.get("/", response_model=List[readEmpleado])
def get_empleados(session: Session = Depends(get_session)):
    statement = select(Empleados)
    results = session.exec(statement).all()
    return results

@router.get("/{id_emp}", response_model=readEmpleado)
def get_empleado(id_emp: int, session: Session = Depends(get_session)):
    empleado = session.get(nombre, id_emp)
    if not empleado:
        return {"error": "Empleado no encontrado"}
    return empleado
