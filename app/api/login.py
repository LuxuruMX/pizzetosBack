from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Dict

from app.db.session import get_session
from app.models.empleadoModel import Empleados

from app.models.permisosModel import permisos as Permisos

from app.core.auth import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES

from datetime import timedelta

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


def serialize_permisos(permiso_obj) -> Dict[str, bool]:
    permisos_dict = {}
    for field_name, field_info in permiso_obj.model_fields.items():
        if field_info.annotation == bool and field_name not in {"id_permiso", "id_cargo"}:
            permisos_dict[field_name] = getattr(permiso_obj, field_name, False)
    return permisos_dict



from sqlmodel import select

@router.post("/", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    empleado = session.exec(select(Empleados).where(Empleados.nickName == form_data.username)).first()
    if not empleado or not verify_password(empleado.password, form_data.password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")


    if empleado.status == 0:
        raise HTTPException(status_code=401, detail="Tu usuario está desactivado")

    permisos_obj = session.exec(
        select(Permisos).where(Permisos.id_cargo == empleado.id_ca)
    ).first()

    if not permisos_obj:
        raise HTTPException(status_code=500, detail="No se encontraron permisos para este cargo")

    permisos_dict = serialize_permisos(permisos_obj)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": empleado.nickName,
            "id_emp": empleado.id_emp,
            "id_cargo": empleado.id_ca,
            "permisos": permisos_dict,
            "sucursal": empleado.id_suc
        },
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}