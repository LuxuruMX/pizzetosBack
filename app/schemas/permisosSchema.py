from pydantic import BaseModel, Field


class readPermisos(BaseModel):
    id_permiso: int
    id_cargo: int
    
    crear_producto:bool
    modificar_producto:bool
    eliminar_producto:bool
    ver_producto:bool
    
    crear_empleado:bool
    modificar_empleado:bool
    eliminar_empleado:bool
    ver_empleado:bool
    
    crear_venta:bool
    modificar_venta:bool
    eliminar_venta:bool
    ver_ventas:bool
    
    crear_recurso:bool 
    modificar_recurso:bool
    eliminar_recurso:bool
    ver_recurso:bool


class readPermisosWhitCargo(BaseModel):
    id_permiso: int
    id_cargo: int
    cargo: str

    crear_producto: bool
    modificar_producto: bool
    eliminar_producto: bool
    ver_producto: bool

    crear_empleado: bool
    modificar_empleado: bool
    eliminar_empleado: bool
    ver_empleado: bool

    crear_venta: bool
    modificar_venta: bool
    eliminar_venta: bool
    ver_venta: bool

    crear_recurso: bool
    modificar_recurso: bool
    eliminar_recurso: bool
    ver_recurso: bool


class createCargoConPermisos(BaseModel):
    nombre: str = Field(min_length=5, max_length=100)
    
    crear_producto: bool = False
    modificar_producto: bool = False
    eliminar_producto: bool = False
    ver_producto: bool = False
    
    crear_empleado: bool = False
    modificar_empleado: bool = False
    eliminar_empleado: bool = False
    ver_empleado: bool = False
    
    crear_venta: bool = False
    modificar_venta: bool = False
    eliminar_venta: bool = False
    ver_venta: bool = False
    
    crear_recurso: bool = False
    modificar_recurso: bool = False
    eliminar_recurso: bool = False
    ver_recurso: bool = False