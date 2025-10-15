# app/core/permissions.py
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.empleadoModel import Empleados
from app.models.permisosModel import permisos as Permisos  
from app.core.dependency import verify_token, TokenData


def get_user_permissions(user_id: int, session: Session) -> dict:
    """
    Obtiene los permisos del empleado desde la tabla Permisos.
    """
    # Buscar empleado
    empleado = session.get(Empleados, user_id)
    if not empleado:
        return {}
    
    # Buscar permisos por id_cargo
    statement = select(Permisos).where(Permisos.id_cargo == empleado.id_ca)
    permisos = session.exec(statement).first()
    
    if not permisos:
        return {}
    
    # Retornar diccionario con todos los permisos
    return {
        "crear_producto": permisos.crear_producto,
        "modificar_producto": permisos.modificar_producto,
        "eliminar_producto": permisos.eliminar_producto,
        "ver_producto": permisos.ver_producto,
        "crear_empleado": permisos.crear_empleado,
        "modificar_empleado": permisos.modificar_empleado,
        "eliminar_empleado": permisos.eliminar_empleado,
        "ver_empleado": permisos.ver_empleado,
        "crear_venta": permisos.crear_venta,
        "modificar_venta": permisos.modificar_venta,
        "eliminar_venta": permisos.eliminar_venta,
        "ver_venta": permisos.ver_venta,
        "crear_recurso": permisos.crear_recurso,
        "modificar_recurso": permisos.modificar_recurso,
        "eliminar_recurso": permisos.eliminar_recurso,
        "ver_recurso": permisos.ver_recurso,
    }


def require_permission(permission_name: str):
    """
    Dependency que verifica si el usuario tiene un permiso específico.
    """
    def permission_checker(
        token_data: TokenData = Depends(verify_token),
        session: Session = Depends(get_session)
    ):
        # Obtener permisos del usuario
        permisos = get_user_permissions(token_data.user_id, session)
        
        # Verificar si tiene el permiso
        if not permisos.get(permission_name, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso para: {permission_name}"
            )
        
        return True
    
    return permission_checker


# BONUS: Funciones para múltiples permisos
def require_any_permission(*permission_names: str):
    """Verifica que el usuario tenga AL MENOS UNO de los permisos."""
    def permission_checker(
        token_data: TokenData = Depends(verify_token),
        session: Session = Depends(get_session)
    ):
        permisos = get_user_permissions(token_data.user_id, session)
        
        has_permission = any(
            permisos.get(perm, False) for perm in permission_names
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Necesitas uno de estos permisos: {', '.join(permission_names)}"
            )
        
        return True
    
    return permission_checker


def require_all_permissions(*permission_names: str):
    """Verifica que el usuario tenga TODOS los permisos."""
    def permission_checker(
        token_data: TokenData = Depends(verify_token),
        session: Session = Depends(get_session)
    ):
        permisos = get_user_permissions(token_data.user_id, session)
        
        missing_perms = [
            perm for perm in permission_names 
            if not permisos.get(perm, False)
        ]
        
        if missing_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Te faltan estos permisos: {', '.join(missing_perms)}"
            )
        
        return True
    
    return permission_checker