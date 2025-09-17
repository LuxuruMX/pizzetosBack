from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel

from app.db.session import get_session
from app.models.empleadoModel import Empleados
from app.core.auth import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES

from datetime import timedelta

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    statement = select(Empleados).where(Empleados.nickName == form_data.username)
    empleado = session.exec(statement).first()
    if not empleado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    if not verify_password(empleado.password, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": empleado.nickName}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}



