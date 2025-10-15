from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from pydantic import BaseModel
from typing import Optional

SECRET_KEY = "qscesz"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None  # ← Agregar esto
    id_cargo: Optional[int] = None  # ← Opcional, pero útil

def verify_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")  # ← Agregar esto
        
        if username is None or user_id is None:  # ← Validar ambos
            raise credentials_exception
            
        return TokenData(
            username=username,
            user_id=user_id  # ← Agregar esto
        )
    except InvalidTokenError:
        raise credentials_exception