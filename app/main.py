from fastapi import FastAPI, Depends
from app.db.session import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.core.dependency import verify_token

from app.api import (login, 
                    empleados,
                    clientes,
                    ventas,
                    recursos,
                    gastos,
                    pos,
                    priceProducts,
                    caja)


app = FastAPI(
    title="Pizzetos",
    description="Backend de pizzetos bien chingon",
    version="1.5.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/check", tags=["Check"])
def check_token(username: str = Depends(verify_token)):
    return {"valid": True, "username": username.username}



app.include_router(login.router, prefix="/login", tags=["login"])
app.include_router(empleados.router, prefix="/empleados", tags=["personal"])
app.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
app.include_router(ventas.router, prefix="/ventas", tags=["ventas"])
app.include_router(recursos.router, prefix="/recursos", tags=["recursos"])
app.include_router(gastos.router, prefix="/gastos", tags=["gastos"])
app.include_router(pos.router, prefix="/pos", tags=["punto de venta"])
app.include_router(priceProducts.router, prefix="/prices", tags=["precios productos"])
app.include_router(caja.router, prefix="/caja", tags=["caja"])