from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session

from app.models.detallesModel import DetalleVenta
from app.models.ventaModel import Venta

from app.schemas.detallesSchema import readDetalleVenta, createDetalleVenta
from app.schemas.ventaSchema import readVenta, createVenta

from app.models.sucursalModel import Sucursal

router = APIRouter()


@router.get("/")
def getGastos(session: Session = Depends(get_session)):
    pass