from sqlmodel import SQLModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.sql import func

class Gastos(SQLModel, table=True):
    __tablename__="Gastos"
    id_gastos: Optional[int] = Field(default=None, primary_key=True)
    id_suc: int
    descripcion: str = Field(min_length=3, max_length=255)
    precio: Decimal
    fecha: Optional[datetime] = Field(default=None, sa_column_kwargs={"server_default": func.now()})
    evaluado: Optional[bool] = Field(default=False)