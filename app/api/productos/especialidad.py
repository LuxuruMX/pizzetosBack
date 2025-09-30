from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token


from app.models.especialidadModel import especialidad
from app.schemas.especialidadSchema import createEspecialidad, readEspecialidad

from app.models.categoriaModel import categoria as CategoriasProd

router = APIRouter()




@router.get("/especialidades",response_model=List[readEspecialidad] ,tags=["Especialidad"])
def getEspecialidades(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(especialidad)
    results = session.exec(statement).all()
    return results


@router.get("/especialidades/{id_esp}", response_model=readEspecialidad, tags=["Especialidad"])
def getEspecialidadById(id_esp: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    especialidad_item = session.get(especialidad, id_esp)
    if especialidad_item:
        return especialidad_item
    return {"message": "Especialidad no encontrada"}

@router.put("/actualizar-especialidad/{id_esp}", tags=["Especialidad"])
def updateEspecialidad(id_esp: int, especialidad_data: createEspecialidad, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    especialidad_item = session.get(especialidad, id_esp)
    if not especialidad_item:
        return {"message": "Especialidad no encontrada"}
    
    especialidad_item.nombre = especialidad_data.nombre
    especialidad_item.descripcion = especialidad_data.descripcion
    
    session.add(especialidad_item)
    session.commit()
    session.refresh(especialidad_item)
    
    return {"message": "Especialidad actualizada correctamente"}


@router.post("/crear-especialidad", tags=["Especialidad"])
def createEspecialidad(especialidad_data: createEspecialidad, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    nueva_especialidad = especialidad(
        nombre= especialidad_data.nombre,
        descripcion= especialidad_data.descripcion
    )
    session.add(nueva_especialidad)
    session.commit()
    session.refresh(nueva_especialidad)
    return {"message": "Especialidad registrada correctamente"}


@router.delete("/eliminar-especialidad/{id_esp}", tags=["Especialidad"])
def deleteEspecialidad(id_esp: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    especialidad_item = session.get(especialidad, id_esp)
    if not especialidad_item:
        return {"message": "Especialidad no encontrada"}
    session.delete(especialidad_item)
    session.commit()
    return {"message": "Especialidad eliminada correctamente"}

