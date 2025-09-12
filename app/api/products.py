from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def products():
    return {"message": "Mensaje"}


@router.get("/{Id_product}")
def product(Id_product: int):
    return {"message": Id_product}

@router.put("/agregar")
def agregar(aaa: int):
    return {"message": aaa}

@router.put("/eliminar")
def eliminar():
    pass

@router.delete("/definitivo")
def definivo():
    pass


