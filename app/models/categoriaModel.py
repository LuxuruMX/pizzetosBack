from typing import Optional
from sqlmodel import SQLModel, Field


class categoria(SQLModel, table=True):
    __tablename__ = "CategoriasProd"
    id_cat: Optional[int] = Field(default=None, primary_key=True)
    descripcion: str = Field(min_length=5, max_length=100)