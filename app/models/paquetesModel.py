from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Numeric


class paquete1(SQLModel, table=True):
    __tablename__ = "Paquete1"
    id_paquete1: Optional[int] = Field(default=None, primary_key=True)
    id_especialidad: int = Field(foreign_key="Especialidades.id_esp", nullable=False)
    id_refresco: int = Field(foreign_key="Refrescos.id_refresco", nullable=False)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    
    
class paquete2(SQLModel, table=True):
    __tablename__ = "Paquete2"
    id_paquete2: Optional[int] = Field(default=None, primary_key=True)
    id_especialidad: int = Field(foreign_key="Especialidades.id_esp", nullable=False)
    id_alitas: int = Field(foreign_key="Alitas.id_alis", nullable=False)
    id_hamburguesa: int = Field(foreign_key="Hamburguesas.id_hamb", nullable=False)
    id_refresco: int = Field(foreign_key="Refrescos.id_refresco", nullable=False)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    
class paquete3(SQLModel, table=True):
    __tablename__ = "Paquete3"
    id_paquete3: Optional[int] = Field(default=None, primary_key=True)
    id_especialidad: int = Field(foreign_key="Especialidades.id_esp", nullable=False)
    id_refresco: int = Field(foreign_key="Refrescos.id_refresco", nullable=False)
    precio: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))