from datetime import datetime, timedelta
import jwt
from argon2 import PasswordHasher, exceptions as argon2_exceptions

SECRET_KEY = "qscesz"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora

ph = PasswordHasher()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(hashed_password: str, plain_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except argon2_exceptions.VerifyMismatchError:
        return False


