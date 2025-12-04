from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from sqlalchemy import func
from fastapi import HTTPException, status

from app.db.session import get_session
from app.models.clienteModel import Cliente
from app.models.DireccionesModel import Direccion as direccion
from app.schemas.clienteSchema import (readCliente,
                                       createCliente,
                                       readClientePOS,
                                       createDireccionNested,
                                       readDireccion,
                                       ClienteConDirecciones,
                                       DireccionResponse,
                                       updateCliente,
                                       onlyDireccion)

from app.core.permissions import require_permission, require_any_permission

router=APIRouter()


@router.get("/posclientes", response_model=List[readClientePOS])
def getClientesPOS(session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_venta", "crear_venta"))):
    statement=(
        select(Cliente.id_clie, 
               func.concat(Cliente.nombre," ", Cliente.apellido).label("nombre"))
        .order_by(Cliente.nombre)
    )
    results = session.exec(statement).all()
    return results



@router.get("/", response_model=List[readCliente])
def getClientes(session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_venta", "crear_venta"))):
    statement=select(Cliente)
    results = session.exec(statement).all()
    return results



@router.post("/")
def create_Cliente(
    cliente: createCliente, 
    session: Session = Depends(get_session), 
    _: None = Depends(require_permission("crear_venta"))
):
    try:
        # 1. Crear el cliente
        nuevo_cliente = Cliente(
            nombre=cliente.nombre,
            apellido=cliente.apellido,
            telefono=cliente.telefono
        )
        session.add(nuevo_cliente)
        session.flush() 
        
        if cliente.direcciones:
            for dir_data in cliente.direcciones:
                nueva_direccion = direccion(
                    id_clie=nuevo_cliente.id_clie,
                    calle=dir_data.calle,
                    manzana=dir_data.manzana,
                    lote=dir_data.lote,
                    colonia=dir_data.colonia,
                    referencia=dir_data.referencia
                )
                session.add(nueva_direccion)
        
        session.commit()
        session.refresh(nuevo_cliente)
        
        # ✅ CAMBIO: Devolver el cliente creado con su ID
        return {
            "Message": "Cliente y direcciones creadas exitosamente",
            "id_clie": nuevo_cliente.id_clie,
            "nombre": nuevo_cliente.nombre,
            "apellido": nuevo_cliente.apellido,
            "telefono": nuevo_cliente.telefono
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al crear cliente y direcciones: {str(e)}"
        )



@router.post("/{id_clie}/direcciones", response_model=readDireccion)
def addDireccionCliente(
    id_clie: int,
    direccion_data: createDireccionNested,
    session: Session = Depends(get_session),
    _: None = Depends(require_permission("crear_venta"))
):
    try:
        # 1. Verificar que el cliente existe
        cliente_existente = session.get(Cliente, id_clie)
        if not cliente_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con id {id_clie} no encontrado"
            )
        
        # 2. Crear la nueva dirección
        nueva_direccion = direccion(
            id_clie=id_clie,
            calle=direccion_data.calle,
            manzana=direccion_data.manzana,
            lote=direccion_data.lote,
            colonia=direccion_data.colonia,
            referencia=direccion_data.referencia
        )
        
        session.add(nueva_direccion)
        session.commit()
        session.refresh(nueva_direccion)
        
        return nueva_direccion
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al agregar dirección: {str(e)}"
        )



@router.get("/{id_clie}", response_model=ClienteConDirecciones)
def getClienteConDirecciones(
    id_clie: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_any_permission("ver_venta", "crear_venta"))
):
    # 1. Buscar el cliente
    cliente = session.get(Cliente, id_clie)
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con id {id_clie} no encontrado"
        )
    
    # 2. Buscar todas las direcciones del cliente
    statement = select(direccion).where(direccion.id_clie == id_clie)
    direcciones_cliente = session.exec(statement).all()
    
    # 3. Construir la respuesta
    return ClienteConDirecciones(
        id_clie=cliente.id_clie,
        nombre=cliente.nombre,
        apellido=cliente.apellido,
        telefono=cliente.telefono,
        direcciones=[
            DireccionResponse(
                id_dir=dir.id_dir,
                calle=dir.calle,
                manzana=dir.manzana,
                lote=dir.lote,
                colonia=dir.colonia,
                referencia=dir.referencia
            )
            for dir in direcciones_cliente
        ]
    )



@router.get("/direccion/{id_clie}", response_model=List[onlyDireccion])
def getDireccion(
    id_clie: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_any_permission("ver_venta", "crear_venta", "editar_venta"))
):    
    # 2. Buscar todas las direcciones del cliente
    statement = select(direccion).where(direccion.id_clie == id_clie)
    direcciones_cliente = session.exec(statement).all()
    
    return [
            onlyDireccion(
                id_dir=dir.id_dir,
                calle=dir.calle,
                manzana=dir.manzana,
                lote=dir.lote,
                colonia=dir.colonia,
                referencia=dir.referencia
            )
            for dir in direcciones_cliente
        ]



@router.put("/{id_clie}", response_model=ClienteConDirecciones)
def updateClienteConDirecciones(
    id_clie: int,
    cliente_data: updateCliente,
    session: Session = Depends(get_session),
    _: None = Depends(require_any_permission("editar_venta", "crear_venta"))
):
    try:
        # 1. Verificar que el cliente existe
        cliente = session.get(Cliente, id_clie)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente con id {id_clie} no encontrado"
            )
        
        # 2. Actualizar datos del cliente (solo los que se envíen)
        if cliente_data.nombre is not None:
            cliente.nombre = cliente_data.nombre
        if cliente_data.apellido is not None:
            cliente.apellido = cliente_data.apellido
        if cliente_data.telefono is not None:
            cliente.telefono = cliente_data.telefono
        
        session.add(cliente)
        
        # 3. Manejar las direcciones si se envían
        if cliente_data.direcciones is not None:
            # Obtener IDs de direcciones existentes del cliente
            statement = select(direccion).where(direccion.id_clie == id_clie)
            direcciones_existentes = session.exec(statement).all()
            ids_existentes = {dir.id_dir for dir in direcciones_existentes}
            
            # IDs de direcciones que se están actualizando/manteniendo
            ids_enviados = {dir.id_dir for dir in cliente_data.direcciones if dir.id_dir is not None}
            
            # Eliminar direcciones que no se enviaron (fueron removidas)
            ids_a_eliminar = ids_existentes - ids_enviados
            for id_dir in ids_a_eliminar:
                dir_a_eliminar = session.get(direccion, id_dir)
                if dir_a_eliminar:
                    session.delete(dir_a_eliminar)
            
            # Actualizar o crear direcciones
            for dir_data in cliente_data.direcciones:
                if dir_data.id_dir:
                    # Actualizar dirección existente
                    dir_existente = session.get(direccion, dir_data.id_dir)
                    if dir_existente and dir_existente.id_clie == id_clie:
                        dir_existente.calle = dir_data.calle
                        dir_existente.manzana = dir_data.manzana
                        dir_existente.lote = dir_data.lote
                        dir_existente.colonia = dir_data.colonia
                        dir_existente.referencia = dir_data.referencia
                        session.add(dir_existente)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Dirección con id {dir_data.id_dir} no encontrada o no pertenece al cliente"
                        )
                else:
                    # Crear nueva dirección
                    nueva_direccion = direccion(
                        id_clie=id_clie,
                        calle=dir_data.calle,
                        manzana=dir_data.manzana,
                        lote=dir_data.lote,
                        colonia=dir_data.colonia,
                        referencia=dir_data.referencia
                    )
                    session.add(nueva_direccion)
        
        # 4. Confirmar todos los cambios
        session.commit()
        session.refresh(cliente)
        
        # 5. Obtener las direcciones actualizadas
        statement = select(direccion).where(direccion.id_clie == id_clie)
        direcciones_actualizadas = session.exec(statement).all()
        
        # 6. Construir la respuesta
        return ClienteConDirecciones(
            id_clie=cliente.id_clie,
            nombre=cliente.nombre,
            apellido=cliente.apellido,
            telefono=cliente.telefono,
            direcciones=[
                DireccionResponse(
                    id_dir=dir.id_dir,
                    calle=dir.calle,
                    manzana=dir.manzana,
                    lote=dir.lote,
                    colonia=dir.colonia,
                    referencia=dir.referencia
                )
                for dir in direcciones_actualizadas
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar cliente: {str(e)}"
        )

