from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.dependency import verify_token

from app.models.rectangularModel import rectangular 
from app.schemas.rectangularSchema import readRectangularOut

from app.models.categoriaModel import categoria as CategoriasProd
from app.models.especialidadModel import especialidad

router = APIRouter()


@router.get("/", response_model=List[readRectangularOut])
def getRectangular(session: Session = Depends(get_session), username: str = Depends(verify_token)):
    statement = (
        select(rectangular.id_rec, rectangular.porcion1, rectangular.porcion2, rectangular.porcion3, rectangular.porcion4, especialidad.nombre.label("especialidad"),CategoriasProd.descripcion.label("categoria"))
        .join(CategoriasProd, rectangular.id_cat == CategoriasProd.id_cat)
        .join(especialidad, rectangular.id_esp == especialidad.id_esp)
    )

    results = session.exec(statement).all()
    return [readRectangularOut(
        id_rec=r.id_rec,
        porcion1=r.porcion1,
        porcion2=r.porcion2,
        porcion3=r.porcion3,
        porcion4=r.porcion4,
        especialidad=r.especialidad,
        categoria=r.categoria
    ) for r in results]