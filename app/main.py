from fastapi import FastAPI, Depends
from app.db.session import init_db
from fastapi.middleware.cors import CORSMiddleware
from app.core.dependency import verify_token

from app.api import login, products, movements, empleados, clientes, ventas


app = FastAPI(
    title="Pizzetos",
    description="Backend de pizzetos bien chingon",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/check")
def check_token(username: str = Depends(verify_token)):
    return {"valid": True, "username": username.username}



app.include_router(login.router, prefix="/login", tags=["login"])
app.include_router(products.router, prefix="/product", tags=["products"])
app.include_router(movements.router, prefix="/movements", tags=["movements"])
app.include_router(empleados.router, prefix="/empleados", tags=["personal"])
app.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
app.include_router(ventas.router, prefix="/ventas", tags=["ventas"])