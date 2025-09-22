from sqlmodel import SQLModel, Field
from typing import Optional

class Cargos(SQLModel, table=True):
    __tablename__="Cargos"
    id_ca: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=5, max_length=100)