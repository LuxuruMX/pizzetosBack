from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.empleadoModel import Empleados
from argon2 import PasswordHasher, exceptions as argon2_exceptions
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel

# Configuración JWT
SECRET_KEY = "qscesz"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora



ph = PasswordHasher()
router = APIRouter()

# Schema para el token
class Token(BaseModel):
    access_token: str
    token_type: str

# Función para crear token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # Buscar empleado por nickName
    statement = select(Empleados).where(Empleados.nickName == form_data.username)
    empleado = session.exec(statement).first()
    if not empleado:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    # Verificar contraseña con argon2
    try:
        ph.verify(empleado.password, form_data.password)
    except argon2_exceptions.VerifyMismatchError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    # Crear token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": empleado.nickName}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}
