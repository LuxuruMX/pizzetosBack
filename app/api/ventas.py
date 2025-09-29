from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token


from app.models.alitasModel import alitas as Alita
from app.schemas.alitasSchema import readAlitasOut, createAlitas

from app.models.costillasModel import costillas
from app.schemas.costillasSchema import readCostillasOut, createCostillas

from app.models.especialidadModel import especialidad
from app.schemas.especialidadSchema import createEspecialidad, readEspecialidad

from app.models.hamburguesasModel import hamburguesas
from app.schemas.hamburguesasSchema import createHamburguesas, readHamburguesasOut

from app.models.categoriaModel import categoria as CategoriasProd


router=APIRouter()


@router.get("/categoria", tags=["Categoria"])
def getCategoriaAlitas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(CategoriasProd)
    results = session.exec(statement).all()
    return results


#==============================================================================================================#
##############################Rutas para detalles de Alitas#####################################################
#==============================================================================================================#
@router.get("/alitas", response_model=List[readAlitasOut], tags=["Alitas"])
def getAlitas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(Alita.id_alis, Alita.orden, Alita.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, Alita.id_cat == CategoriasProd.id_cat)
    )

    results = session.exec(statement).all()
    return [readAlitasOut(
        id_alis=r.id_alis,
        orden=r.orden,
        precio=r.precio,
        categoria=r.categoria
    ) for r in results]
    
    
@router.get("/alitas/{id_alis}", response_model=readAlitasOut, tags=["Alitas"])
def getAlitasById(id_alis: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(Alita.id_alis, Alita.orden, Alita.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, Alita.id_cat == CategoriasProd.id_cat)
        .where(Alita.id_alis == id_alis)
    )

    result = session.exec(statement).first()
    if result:
        return readAlitasOut(
            id_alis=result.id_alis,
            orden=result.orden,
            precio=result.precio,
            categoria=result.categoria
        )
    return {"message": "Alitas no encontradas"}
    
    
@router.put("/actualizar-alitas/{id_alis}", tags=["Alitas"])
def updateAlitas(id_alis: int, alitas: createAlitas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    alita = session.get(Alita, id_alis)
    if not alita:
        return {"message": "Alitas no encontradas"}
    alita.orden = alitas.orden
    alita.precio = alitas.precio
    alita.id_cat = alitas.id_cat
    session.add(alita)
    session.commit()
    session.refresh(alita)
    return {"message": "Alitas actualizadas correctamente"}


@router.post("/crear-alitas", tags=["Alitas"])
def createAlitas(alitas: createAlitas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    alita=Alita(
        orden= alitas.orden,
        precio=alitas.precio,
        id_cat=alitas.id_cat
    )
    session.add(alita)
    session.commit()
    session.refresh(alita)
    return {"message" : "Alitas registradas correctamente"}

@router.delete("/eliminar-alitas/{id_alis}", tags=["Alitas"])
def deleteAlitas(id_alis: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    alita = session.get(Alita, id_alis)
    if not alita:
        return {"message": "Alitas no encontradas"}
    session.delete(alita)
    session.commit()
    return {"message": "Alitas eliminadas correctamente"}



#==============================================================================================================#
##############################Rutas para detalles de Costillas##################################################
#==============================================================================================================#

@router.get("/costillas", response_model=List[readCostillasOut], tags=["Costillas"])
def getCostillas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(costillas.id_cos, costillas.orden, costillas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, costillas.id_cat == CategoriasProd.id_cat)
    )

    results = session.exec(statement).all()
    return [readCostillasOut(
        id_cos=r.id_cos,
        orden=r.orden,
        precio=r.precio,
        categoria=r.categoria
    ) for r in results]
    

@router.get("/costillas/{id_cos}", response_model=readCostillasOut, tags=["Costillas"])
def getCostillasById(id_cos: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(costillas.id_cos, costillas.orden, costillas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, costillas.id_cat == CategoriasProd.id_cat)
        .where(costillas.id_cos == id_cos)
    )

    result = session.exec(statement).first()
    if result:
        return readCostillasOut(
            id_cos=result.id_cos,
            orden=result.orden,
            precio=result.precio,
            categoria=result.categoria
        )
    return {"message": "Costillas no encontradas"}



@router.put("/actualizar-costillas/{id_cos}", tags=["Costillas"])
def updateCostillas(id_cos: int, costillas: createCostillas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    costilla = session.get(costillas, id_cos)
    if not costilla:
        return {"message": "Costillas no encontradas"}
    
    costilla.orden = costillas.orden
    costilla.precio = costillas.precio
    costilla.id_cat = costillas.id_cat
    
    session.add(costilla)
    session.commit()
    session.refresh(costilla)
    
    return {"message": "Costillas actualizadas correctamente"}


@router.post("/crear-costillas", tags=["Costillas"])
def createCostilla(costilla: createCostillas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    cost=costillas(
        orden= costilla.orden,
        precio= costilla.precio,
        id_cat= costilla.id_cat
    )
    session.add(cost)
    session.commit()
    session.refresh(cost)
    return {"message": "Costilla registrada orrectamente"}


@router.delete("/eliminar-costillas/{id_cos}", tags=["Costillas"])
def deleteCostillas(id_cos: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    costilla = session.get(costillas, id_cos)
    if not costilla:
        return {"message": "Costillas no encontradas"}
    session.delete(costilla)
    session.commit()
    return {"message": "Costillas eliminadas correctamente"}

#==============================================================================================================#
##############################Rutas para detalles de Especialidades#############################################
#==============================================================================================================#

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


#==============================================================================================================#
##############################Rutas para detalles de Hamburguesas###############################################
#==============================================================================================================#

@router.get("/hamburguesas", response_model=List[readHamburguesasOut] ,tags=["Hamburguesas"])
def getHamburguesas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=(
        select(hamburguesas.id_hamb, hamburguesas.paquete, hamburguesas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, hamburguesas.id_cat == CategoriasProd.id_cat)
    )
    results = session.exec(statement).all()
    return [readHamburguesasOut(
        id_hamb=r.id_hamb,
        paquete=r.paquete,
        precio=r.precio,
        categoria=r.categoria
    ) for r in results]

@router.get("/hamburguesas/{id_hamb}", response_model=readHamburguesasOut, tags=["Hamburguesas"])
def getHamburguesaById(id_hamb: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(hamburguesas.id_hamb, hamburguesas.paquete, hamburguesas.precio, CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, hamburguesas.id_cat == CategoriasProd.id_cat)
        .where(hamburguesas.id_hamb == id_hamb)
    )

    result = session.exec(statement).first()
    if result:
        return readHamburguesasOut(
            id_hamb=result.id_hamb,
            paquete=result.paquete,
            precio=result.precio,
            categoria=result.categoria
        )
    return {"message": "Hamburguesa no encontrada"}

@router.put("/actualizar-hamburguesa/{id_hamb}", tags=["Hamburguesas"])
def updateHamburguesa(id_hamb: int, hamburguesa_data: createHamburguesas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    hamburguesa_item = session.get(hamburguesas, id_hamb)
    if not hamburguesa_item:
        return {"message": "Hamburguesa no encontrada"}
    
    hamburguesa_item.paquete = hamburguesa_data.paquete
    hamburguesa_item.precio = hamburguesa_data.precio
    hamburguesa_item.id_cat = hamburguesa_data.id_cat
    
    session.add(hamburguesa_item)
    session.commit()
    session.refresh(hamburguesa_item)
    
    return {"message": "Hamburguesa actualizada correctamente"}

@router.post("/crear-hamburguesa", tags=["Hamburguesas"])
def createHamburguesa(hamburguesa_data: createHamburguesas, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    nueva_hamburguesa = hamburguesas(
        paquete= hamburguesa_data.paquete,
        precio= hamburguesa_data.precio,
        id_cat= hamburguesa_data.id_cat
    )
    session.add(nueva_hamburguesa)
    session.commit()
    session.refresh(nueva_hamburguesa)
    return {"message": "Hamburguesa registrada correctamente"}

@router.delete("/eliminar-hamburguesa/{id_hamb}", tags=["Hamburguesas"])
def deleteHamburguesa(id_hamb: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    hamburguesa_item = session.get(hamburguesas, id_hamb)
    if not hamburguesa_item:
        return {"message": "Hamburguesa no encontrada"}
    session.delete(hamburguesa_item)
    session.commit()
    return {"message": "Hamburguesa eliminada correctamente"}