from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.clienteModel import Cliente
from app.schemas.clienteSchema import readCliente, createCliente
from app.core.dependency import verify_token

router=APIRouter()

@router.get("/", response_model=List[readCliente])
def getClientes(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(Cliente)
    results = session.exec(statement).all()
    return results

@router.post("/crear-cliente",response_model=List[readCliente])
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