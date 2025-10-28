from typing import Optional
from sqlmodel import SQLModel, Field



class pizzas(SQLModel, table=True):
    __tablename__ = "Pizzas"
    id_pizza: Optional[int] = Field(default=None, primary_key=True)
    id_esp: int = Field(foreign_key="Especialidades.id_esp", nullable=False)
    id_tamano: int = Field(foreign_key="TamanosPizza.id_tamañop", nullable=False)
    id_cat: int = Field(foreign_key="CategoriasProd.id_cat", nullable=False)