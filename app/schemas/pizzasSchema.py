from pydantic import BaseModel



class createPizza(BaseModel):
    id_esp: int
    id_tamano: int
    id_cat: int

class readPizzasOut(BaseModel):
    id_pizza: int
    especialidad: int
    tamaño: int
    categoria: int
    