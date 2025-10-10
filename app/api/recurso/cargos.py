from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.cargoModel import Cargos

from app.models.permisosModel import permisos
from app.schemas.permisosSchema import readPermisosWhitCargo, createCargoConPermisos

from app.models.empleadoModel import Empleados

router = APIRouter()

########################################################################################
@router.get("/", response_model=List[readPermisosWhitCargo])
def getCargo(session: Session = Depends(get_session)):
    statement = (
        select(permisos.id_permiso,
               Cargos.nombre.label("cargo"),
               
               permisos.crear_producto,
               permisos.modificar_producto,
               permisos.eliminar_producto,
               permisos.ver_producto,
               
               permisos.crear_empleado,
               permisos.modificar_empleado,
               permisos.eliminar_empleado,
               permisos.ver_empleado,
               
               permisos.crear_venta,
               permisos.modificar_venta,
               permisos.eliminar_venta,
               permisos.ver_venta,
               
               permisos.crear_recurso,
               permisos.modificar_recurso,
               permisos.eliminar_recurso,
               permisos.ver_recurso)
        .join(Cargos, permisos.id_cargo == Cargos.id_ca)
    )
    results = session.exec(statement).all()
    return [readPermisosWhitCargo(
        id_permiso=r.id_permiso,
        cargo=r.cargo,
        
        crear_producto=r.crear_producto,
        modificar_producto=r.modificar_producto,
        eliminar_producto=r.eliminar_producto,
        ver_producto=r.ver_producto,
        
        crear_empleado=r.crear_empleado,
        modificar_empleado=r.modificar_empleado,
        eliminar_empleado=r.eliminar_empleado,
        ver_empleado=r.ver_empleado,
        
        crear_venta=r.crear_venta,
        modificar_venta=r.modificar_venta,
        eliminar_venta=r.eliminar_venta,
        ver_venta=r.ver_venta,
        
        crear_recurso=r.crear_recurso,
        modificar_recurso=r.modificar_recurso,
        eliminar_recurso=r.eliminar_recurso,
        ver_recurso=r.ver_recurso
        
    ) for r in results]

########################################################################################
@router.get("/{id_ca}", response_model=readPermisosWhitCargo)
def getCargoById (id_ca: int, session: Session = Depends(get_session)):
    statement = (
        select(permisos.id_permiso,
               Cargos.nombre.label("cargo"),
               
               permisos.crear_producto,
               permisos.modificar_producto,
               permisos.eliminar_producto,
               permisos.ver_producto,
               
               permisos.crear_empleado,
               permisos.modificar_empleado,
               permisos.eliminar_empleado,
               permisos.ver_empleado,
               
               permisos.crear_venta,
               permisos.modificar_venta,
               permisos.eliminar_venta,
               permisos.ver_venta,
               
               permisos.crear_recurso,
               permisos.modificar_recurso,
               permisos.eliminar_recurso,
               permisos.ver_recurso)
        .join(Cargos, permisos.id_cargo == Cargos.id_ca)
        .where(Cargos.id_ca == id_ca)
    )
    result = session.exec(statement).first()
    if result:
        return readPermisosWhitCargo(
            id_permiso=result.id_permiso,
            cargo=result.cargo,
            
            crear_producto=result.crear_producto,
            modificar_producto=result.modificar_producto,
            eliminar_producto=result.eliminar_producto,
            ver_producto=result.ver_producto,
            
            crear_empleado=result.crear_empleado,
            modificar_empleado=result.modificar_empleado,
            eliminar_empleado=result.eliminar_empleado,
            ver_empleado=result.ver_empleado,
            
            crear_venta=result.crear_venta,
            modificar_venta=result.modificar_venta,
            eliminar_venta=result.eliminar_venta,
            ver_venta=result.ver_venta,
            
            crear_recurso=result.crear_recurso,
            modificar_recurso=result.modificar_recurso,
            eliminar_recurso=result.eliminar_recurso,
            ver_recurso=result.ver_recurso
        ) 
    return {"Message":"No se encontro el cargo"}


########################################################################################


@router.post("/")
def createCargoConPermiso(
    data: createCargoConPermisos, 
    session: Session = Depends(get_session)
):
    existing_cargo = session.exec(
        select(Cargos).where(Cargos.nombre == data.nombre)
    ).first()
    
    if existing_cargo:
        {"Message":"Ya existe un cargo con ese nombre"}
    
    nuevo_cargo = Cargos(nombre=data.nombre)
    session.add(nuevo_cargo)
    session.commit()
    session.refresh(nuevo_cargo)
    
    nuevo_permiso = permisos(
        id_cargo=nuevo_cargo.id_ca,
        
        crear_producto=data.crear_producto,
        modificar_producto=data.modificar_producto,
        eliminar_producto=data.eliminar_producto,
        ver_producto=data.ver_producto,
        
        crear_empleado=data.crear_empleado,
        modificar_empleado=data.modificar_empleado,
        eliminar_empleado=data.eliminar_empleado,
        ver_empleado=data.ver_empleado,
        
        crear_venta=data.crear_venta,
        modificar_venta=data.modificar_venta,
        eliminar_venta=data.eliminar_venta,
        ver_venta=data.ver_venta,
        
        crear_recurso=data.crear_recurso,
        modificar_recurso=data.modificar_recurso,
        eliminar_recurso=data.eliminar_recurso,
        ver_recurso=data.ver_recurso
    )
    
    session.add(nuevo_permiso)
    session.commit()
    session.refresh(nuevo_permiso)
    
    return {"Message":"Cargo creado con exito"}


@router.put("/{id_ca}")
def updateCargoConPermisos(
    id_ca: int,
    data: createCargoConPermisos, 
    session: Session = Depends(get_session)
):
    cargo = session.get(Cargos, id_ca)
    if not cargo:
        return {"Message":"No se encontro el cargo"}
    
    existing_cargo = session.exec(
        select(Cargos).where(Cargos.nombre == data.nombre, Cargos.id_ca != id_ca)
    ).first()
    
    if existing_cargo:
        return {"Message":"Ya existe ese nombre en otro cargo"}
    
    cargo.nombre = data.nombre
    session.add(cargo)
    session.commit()
    session.refresh(cargo)
    
    permiso = session.exec(
        select(permisos).where(permisos.id_cargo == id_ca)
    ).first()
    
    if not permiso:
        permiso = permisos(
            id_cargo=id_ca,
            
            crear_producto=data.crear_producto,
            modificar_producto=data.modificar_producto,
            eliminar_producto=data.eliminar_producto,
            ver_producto=data.ver_producto,
            
            crear_empleado=data.crear_empleado,
            modificar_empleado=data.modificar_empleado,
            eliminar_empleado=data.eliminar_empleado,
            ver_empleado=data.ver_empleado,
            
            crear_venta=data.crear_venta,
            modificar_venta=data.modificar_venta,
            eliminar_venta=data.eliminar_venta,
            ver_venta=data.ver_venta,
            
            crear_recurso=data.crear_recurso,
            modificar_recurso=data.modificar_recurso,
            eliminar_recurso=data.eliminar_recurso,
            ver_recurso=data.ver_recurso
        )
    else:
        permiso.crear_producto = data.crear_producto
        permiso.modificar_producto = data.modificar_producto
        permiso.eliminar_producto = data.eliminar_producto
        permiso.ver_producto = data.ver_producto
        
        permiso.crear_empleado = data.crear_empleado
        permiso.modificar_empleado = data.modificar_empleado
        permiso.eliminar_empleado = data.eliminar_empleado
        permiso.ver_empleado = data.ver_empleado
        
        permiso.crear_venta = data.crear_venta
        permiso.modificar_venta = data.modificar_venta
        permiso.eliminar_venta = data.eliminar_venta
        permiso.ver_venta = data.ver_venta
        
        permiso.crear_recurso = data.crear_recurso
        permiso.modificar_recurso = data.modificar_recurso
        permiso.eliminar_recurso = data.eliminar_recurso
        permiso.ver_recurso = data.ver_recurso
    
    session.add(permiso)
    session.commit()
    session.refresh(permiso)
    
    return {"Message":"Actualizado exitosamente"}
    

@router.delete("/{id_ca}")
def deleteCargoConPermisos(
    id_ca: int,
    session: Session = Depends(get_session)
):
    cargo = session.get(Cargos, id_ca)
    if not cargo:
        return {"Message":"No se encontro el cargo"}
    
    empleados_con_cargo = session.exec(
        select(Empleados).where(Empleados.id_ca == id_ca)
    ).first()
    
    if empleados_con_cargo:
        return {"Message":"No se puede eliminar, exite personal con ese cargo"}
    
    permisos_cargo = session.exec(
        select(permisos).where(permisos.id_cargo == id_ca)
    ).all()
    
    for permiso in permisos_cargo:
        session.delete(permiso)
    
    session.commit()
    
    session.delete(cargo)
    session.commit()
    
    return {"message": "Cargo y permisos eliminados correctamente"}