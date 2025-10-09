from fastapi import FastAPI, Depends
from app.db.session import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.core.dependency import verify_token

from app.api import (login, 
                    empleados,
                    clientes,
                    recursos,
                    ventas)


app = FastAPI(
    title="Pizzetos",
    description="Backend de pizzetos bien chingon",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
app.include_router(recursos.router, prefix="/extras", tags=["extras"])