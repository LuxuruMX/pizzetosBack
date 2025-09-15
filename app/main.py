from fastapi import FastAPI
from app.db.session import init_db

from app.api import sessions
from app.api import products
from app.api import movements
from app.api import empleados

app = FastAPI(
    title="Pizzetos",
    description="Backend de pizzetos bien chingon",
    version="0.0.1"
)

@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["Home"])
def root():
    return {"message": "API funcionando correctamente"}



app.include_router(sessions.router, prefix="/login", tags=["sessions"])
app.include_router(products.router, prefix="/product", tags=["products"])
app.include_router(movements.router, prefix="/movements", tags=["movements"])
app.include_router(empleados.router, prefix="/empleados", tags=["personal"])