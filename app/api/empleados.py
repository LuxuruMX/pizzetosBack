from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.empleadoModel import Empleados
from app.schemas.empleadoSchema import readEmpleadoNoPass, createEmpleado
from argon2 import PasswordHasher
from app.core.dependency import verify_token

from app.models.cargoModel import Cargos
from app.schemas.cargoSchema import readCargo

from app.models.sucursalModel import Sucursal


router = APIRouter()
ph = PasswordHasher()


@router.get("/cargo", response_model=List[readCargo])
def getCargos(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = select(Cargos)
    results = session.exec(statement).all()
    return results



@router.get("/", response_model=List[readEmpleadoNoPass])
def get_empleados(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(Empleados.id_emp,Empleados.nombre, Empleados.direccion, Empleados.telefono, Cargos.nombre.label("cargo"), Sucursal.nombre.label("sucursal"), Empleados.nickName, Empleados.status)
        .join(Cargos, Empleados.id_ca == Cargos.id_ca)
        .join(Sucursal, Empleados.id_suc == Sucursal.id_suc)
    )
    results = session.exec(statement).all()
    return results

@router.get("/{id_emp}", response_model=readEmpleadoNoPass)
def getEmpleadoById(id_emp: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(Empleados.id_emp,Empleados.nombre, Empleados.direccion, Empleados.telefono, Cargos.nombre.label("cargo"), Sucursal.nombre.label("sucursal"), Empleados.nickName, Empleados.status)
        .join(Cargos, Empleados.id_ca == Cargos.id_ca)
        .join(Sucursal, Empleados.id_suc == Sucursal.id_suc)
        .where(Empleados.id_emp == id_emp)
    )
    
    result = session.exec(statement).first()
    if result:
        return readEmpleadoNoPass(
            id_emp=result.id_emp,
            nombre=result.nombre,
            direccion=result.direccion,
            telefono=result.telefono,
            cargo=result.cargo,
            sucursal=result.sucursal,
            nickName=result.nickName,
            status=result.status
        )
    return {"message":"No se encontro el empleado"}


@router.post("/")
def addEmpleado(empleado: createEmpleado, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    hashed_password = ph.hash(empleado.password) if empleado.password else None
    
    db_empleado = Empleados(
        nombre=empleado.nombre,
        direccion=empleado.direccion,
        telefono=empleado.telefono,
        id_ca=empleado.id_ca,
        id_suc=empleado.id_suc,
        nickName=empleado.nickName,
        password=hashed_password,
        status=empleado.status
    )
    session.add(db_empleado)
    session.commit()
    session.refresh(db_empleado)
    return {"message" : "usuario registrado"}


@router.put("/{id_emp}", response_model=readEmpleadoNoPass)
def updateEmpleado(
    id_emp: int, 
    empleado: createEmpleado, 
    session: Session = Depends(get_session), 
    username: str = Depends(verify_token)
):
    db_empleado = session.get(Empleados, id_emp)
    if not db_empleado:
        {"Message":"No se encontro el empleado"}
    
    db_empleado.nombre = empleado.nombre
    db_empleado.direccion = empleado.direccion
    db_empleado.telefono = empleado.telefono
    db_empleado.id_ca = empleado.id_ca
    db_empleado.id_suc = empleado.id_suc
    
    # Solo actualizar nickname si se proporciona
    if empleado.nickName:
        db_empleado.nickName = empleado.nickName
    
    db_empleado.status = empleado.status
    
    # Solo actualizar password si se proporciona uno nuevo
    if empleado.password:
        db_empleado.password = ph.hash(empleado.password)
    
    session.add(db_empleado)
    session.commit()
    session.refresh(db_empleado)
    
    # Obtener los nombres de cargo y sucursal
    cargo = session.get(Cargos, db_empleado.id_ca)
    sucursal = session.get(Sucursal, db_empleado.id_suc)
    
    # Construir la respuesta con los nombres
    return readEmpleadoNoPass(
        id_emp=db_empleado.id_emp,
        nombre=db_empleado.nombre,
        direccion=db_empleado.direccion,
        telefono=db_empleado.telefono,
        cargo=cargo.nombre if cargo else "",
        sucursal=sucursal.nombre if sucursal else "",
        nickName=db_empleado.nickName,
        status=db_empleado.status
    )


@router.patch("/{id_emp}")
def toggleEmpleadoStatus(
    id_emp: int,
    session: Session = Depends(get_session),
    username: str = Depends(verify_token)
):
    db_empleado = session.get(Empleados, id_emp)
    if not db_empleado:
        return {"Message":"No se encontro al empleado"}

    db_empleado.status = not db_empleado.status

    session.add(db_empleado)
    session.commit()
    session.refresh(db_empleado)

    return {
        "message": f"Empleado {'activado' if db_empleado.status else 'desactivado'}",
        "status": db_empleado.status
    }
    
@router.delete("/{id_emp}")
def deleteEmpleado(
    id_emp: int, 
    session: Session = Depends(get_session), 
    username: str = Depends(verify_token)
):
    db_empleado = session.get(Empleados, id_emp)
    if not db_empleado:
        return {"Message":"No se encontro al empleado"}
    
    session.delete(db_empleado)
    session.commit()
    
    return {"message": "Empleado eliminado correctamente"}

