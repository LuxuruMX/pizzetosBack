from typing import Optional
from sqlmodel import SQLModel, Field


class permisos(SQLModel, table=True):
    __tablename__ = "Permisos"
    id_permiso: Optional[int] = Field(default=None, primary_key=True)
    id_cargo: int = Field(foreign_key="Cargos.id_ca", nullable=False)
    
    crear_producto:bool = Field(default=False)
    modificar_producto:bool = Field(default=False)
    eliminar_producto:bool = Field(default=False)
    ver_producto:bool = Field(default=False)
    
    crear_empleado:bool = Field(default=False)
    modificar_empleado:bool = Field(default=False)
    eliminar_empleado:bool = Field(default=False)
    ver_empleado:bool = Field(default=False)
    
    crear_venta:bool = Field(default=False)
    modificar_venta:bool = Field(default=False)
    eliminar_venta:bool = Field(default=False)
    ver_venta:bool = Field(default=False)
    
    crear_recurso:bool = Field(default=False)
    modificar_recurso:bool = Field(default=False)
    eliminar_recurso:bool = Field(default=False)
    ver_recurso:bool = Field(default=False)
