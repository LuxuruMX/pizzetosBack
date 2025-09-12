from fastapi import FastAPI


# Crear la app FastAPI
app = FastAPI(
    title="Pizzetos",
    description="Backend de pizzetos bien chingon",
    version="0.0.1"
)



@app.get("/")
def root():
    return {"message": "API funcionando correctamente ✅"}
