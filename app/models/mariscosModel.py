from typing import Optional
from sqlmodel import SQLModel, Field



class mariscos(SQLModel, table=True):
    __tablename__ = "PizzasMariscos"
    id_maris: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=5, max_length=100)
    descripcion: str = Field(min_length=5, max_length=200)
    id_tamañop: int = Field(foreign_key="TamanosPizza.id_tamañop", nullable=False)
    id_cat: int = Field(foreign_key="CategoriasProd.id_cat", nullable=False)