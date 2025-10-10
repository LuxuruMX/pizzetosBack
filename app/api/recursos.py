from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from argon2 import PasswordHasher
from app.core.dependency import verify_token

from app.api.recurso import (cargos,
                             sucursales)

router = APIRouter()
ph = PasswordHasher()



router.include_router(cargos.router, prefix="/cargos", tags=["cargos"])
router.include_router(sucursales.router, prefix="/sucursales", tags=["Sucursales"])