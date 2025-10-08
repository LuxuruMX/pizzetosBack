from typing import Optional
from sqlmodel import SQLModel, Field


class permisos(SQLModel, table=True):
    __tablename__ = "Permisos"
    id_permiso: Optional[int] = Field(default=None, primary_key=True)
    id_cargo: int = Field(foreign_key="Cargos.id_ca", nullable=False)
    crear_productos:bool = Field(default=False)
    modificar_productos:bool = Field(default=False)
    eliminar_productos:bool = Field(default=False)
    crear_empleado:bool = Field(default=False)
    modificar_empleado:bool = Field(default=False)
    eliminar_empleado:bool = Field(default=False)
    crear_venta:bool = Field(default=False)
    modificar_venta:bool = Field(default=False)
    eliminar_venta:bool = Field(default=False)
    crear_extras:bool = Field(default=False)
    modificar_extras:bool = Field(default=False)
    eliminar_extras:bool = Field(default=False)
    ver_productos:bool = Field(default=False)
    ver_empleados:bool = Field(default=False)
    ver_ventas:bool = Field(default=False)
    ver_extras:bool = Field(default=False)
