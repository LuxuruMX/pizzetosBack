from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def movements():
    pass

@router.get("/{Id_Sucursal}")
def sucursal():
    pass

@router.get("/{sucursal}/ventas")
def ventas():
    pass

@router.get("/{sucursal}/gastos")
def gastos():
    pass

@router.get("/{sucursal}/beneficio")
def beneficio():
    pass

@router.get("/{sucursal}/crecimiento")
def crecimiento():
    pass

@router.get("/imprimir")
def imprimir():
    pass