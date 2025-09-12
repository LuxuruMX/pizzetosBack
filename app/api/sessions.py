from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
def register(user: dict):
    return {"message": f"Usuario {user['username']} registrado"}

@router.post("/login")
def login(user: dict):
    return {"message": f"Usuario {user['username']} logueado"}
