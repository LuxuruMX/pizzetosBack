from fastapi import FastAPI

from app.api import sessions
from app.api import products



app = FastAPI(
    title="Pizzetos",
    description="Backend de pizzetos bien chingon",
    version="0.0.1"
)



@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}



app.include_router(sessions.router, prefix="/login", tags=["sessions"])
app.include_router(products.router, prefix="/product", tags=["products"])