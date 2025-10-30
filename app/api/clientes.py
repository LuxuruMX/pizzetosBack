from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from sqlalchemy import func

from app.db.session import get_session
from app.models.clienteModel import Cliente
from app.schemas.clienteSchema import readCliente, createCliente, readClientePOS
from app.core.dependency import verify_token

router=APIRouter()


@router.get("/posclientes", response_model=List[readClientePOS])
def getClientesPOS(session: Session = Depends(get_session)):
    statement=(
        select(Cliente.id_clie, 
               func.concat(Cliente.nombre," ", Cliente.apellido).label("nombre"))
        .order_by(Cliente.nombre)
    )
    results = session.exec(statement).all()
    return results


@router.get("/", response_model=List[readCliente])
def getClientes(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(Cliente)
    results = session.exec(statement).all()
    return results

@router.post("/crear-cliente")
def createCliente(cliente: createCliente, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    cliente=Cliente(
        nombre=cliente.nombre,
        apellido=cliente.apellido,
        direccion=cliente.direccion,
        telefono=cliente.telefono
    )
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return {"message" : "cliente registrado"}

@router.get("/buscar/{telefono}", response_model=readCliente)
def searchCliente(telefono: int, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(Cliente).where(Cliente.telefono == telefono)
    results = session.exec(statement).first()
    return results
