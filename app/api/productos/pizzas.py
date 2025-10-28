from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.core.permissions import require_permission, require_any_permission


from app.models.pizzasModel import pizzas
from app.schemas.pizzasSchema import readPizzasOut, createPizza

from app.models.especialidadModel import especialidad
from app.models.tamanosPizzasModel import tamanosPizzas
from app.models.categoriaModel import categoria

router = APIRouter()

@router.get("/", response_model=List[readPizzasOut])
def getPizzas(session: Session = Depends(get_session), _: None = Depends(require_permission("ver_producto"))):
    statement = (
        select(pizzas.id_pizza, especialidad.id_esp.label("especialidad"), tamanosPizzas.id_tamañop.label("tamaño"), categoria.id_cat.label("categoria"))
        .join(especialidad, pizzas.id_esp == especialidad.id_esp)
        .join(tamanosPizzas, pizzas.id_tamano == tamanosPizzas.id_tamañop)
        .join(categoria, pizzas.id_cat == categoria.id_cat)
    )

    results = session.exec(statement).all()
    return [readPizzasOut(
        id_pizza=r.id_pizza,
        especialidad=r.especialidad,
        tamaño=r.tamaño,
        categoria=r.categoria
    ) for r in results]

@router.post("/")
def createNewPizza(pizza: createPizza, session: Session = Depends(get_session), _: None = Depends(require_permission("crear_producto"))):
    new_pizza = pizzas(
        id_esp=pizza.id_esp,
        id_tamano=pizza.id_tamano,
        id_cat=pizza.id_cat
    )
    session.add(new_pizza)
    session.commit()
    session.refresh(new_pizza)
    return {"message": "Pizza creada correctamente"}

@router.put("/{id_pizza}")
def updatePizza(id_pizza: int, pizza: createPizza, session: Session = Depends(get_session), _: None = Depends(require_permission("modificar_producto"))):
    pizza_item = session.get(pizzas, id_pizza)
    if not pizza_item:
        return {"message": "Pizza no encontrada"}
    pizza_item.id_esp = pizza.id_esp
    pizza_item.id_tamano = pizza.id_tamano
    pizza_item.id_cat = pizza.id_cat
    session.add(pizza_item)
    session.commit()
    session.refresh(pizza_item)
    return {"message": "Pizza actualizada correctamente"}

@router.delete("/{id_pizza}")
def deletePizza(id_pizza: int, session: Session = Depends(get_session), _: None = Depends(require_permission("eliminar_producto"))):
    pizza_item = session.get(pizzas, id_pizza)
    if not pizza_item:
        return {"message": "Pizza no encontrada"}
    session.delete(pizza_item)
    session.commit()
    return {"message": "Pizza eliminada correctamente"}

@router.get("/{id_pizza}", response_model=readPizzasOut)
def getPizzaById(id_pizza: int, session: Session = Depends(get_session), _: None = Depends(require_any_permission("ver_producto", "modificar_producto"))):
    statement = (
        select(pizzas.id_pizza, especialidad.id_esp.label("especialidad"), tamanosPizzas.id_tamañop.label("tamaño"), categoria.id_cat.label("categoria"))
        .join(especialidad, pizzas.id_esp == especialidad.id_esp)
        .join(tamanosPizzas, pizzas.id_tamano == tamanosPizzas.id_tamañop)
        .join(categoria, pizzas.id_cat == categoria.id_cat)
        .where(pizzas.id_pizza == id_pizza)
    )

    result = session.exec(statement).first()
    if result:
        return readPizzasOut(
            id_pizza=result.id_pizza,
            especialidad=result.especialidad,
            tamaño=result.tamaño,
            categoria=result.categoria
        )
    return {"message": "Pizza no encontrada"}