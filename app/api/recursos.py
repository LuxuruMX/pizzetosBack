from fastapi import APIRouter
from argon2 import PasswordHasher

from app.api.recurso import (cargos,
                             sucursales,
                             categorias,
                             tamPizza)

router = APIRouter()
ph = PasswordHasher()



router.include_router(cargos.router, prefix="/cargos", tags=["cargos"])
router.include_router(sucursales.router, prefix="/sucursales", tags=["Sucursales"])
router.include_router(categorias.router, prefix="/categorias", tags=["Categorias"])
router.include_router(tamPizza.router, prefix="/tamanos-pizzas", tags=["Tamaños Pizzas"])