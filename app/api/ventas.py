from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.ventaModel import Venta
from app.schemas.ventaSchema import readVenta, createVenta
from app.models.detallesModel import DetalleVenta
from app.schemas.detallesSchema import createDetalleVenta
from app.core.dependency import verify_token


from app.models.alitasModel import alitas as Alita
from app.schemas.alitasSchema import readAlitasOut, createAlitas

from app.models.categoriaModel import categoria as CategoriasProd
from app.schemas.categoriaSchema import readCategoria


router=APIRouter()

@router.get("/", response_model=List[readVenta])
def getVentas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(Venta)
    results = session.exec(statement).all()
    return results

@router.post("/crear-venta")
def createVenta(ventas: createVenta, session: Session = Depends(get_session), username: str = Depends(verify_token)):
    venta=Venta(
        id_suc= ventas.id_suc,
        id_cliente=ventas.id_cliente,
        total=ventas.total
    )
    session.add(venta)
    session.commit()
    session.refresh(venta)
    return {"message" : "Venta registrada correctamente"}




#==============================================================================================================#
##############################Rutas para detalles de Alitas#####################################################
#==============================================================================================================#
@router.get("/alitas", response_model=List[readAlitasOut])
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
    
    
@router.get("/categoria-alitas")
def getCategoriaAlitas(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement=select(CategoriasProd)
    results = session.exec(statement).all()
    return results


@router.post("/crear-alitas")
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