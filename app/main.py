from fastapi import FastAPI
from app.db.session import init_db
from fastapi.middleware.cors import CORSMiddleware


from app.api import login
from app.api import products
from app.api import movements
from app.api import empleados

app = FastAPI(
    title="Pizzetos",
    description="Backend de pizzetos bien chingon",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # o ["*"] para todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["Home"])
def root():
    return {"message": "API funcionando correctamente"}


app.include_router(login.router, prefix="/login", tags=["login"])
app.include_router(products.router, prefix="/product", tags=["products"])
app.include_router(movements.router, prefix="/movements", tags=["movements"])
app.include_router(empleados.router, prefix="/empleados", tags=["personal"])