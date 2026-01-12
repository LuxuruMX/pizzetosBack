"""
Módulo de funciones cacheadas para reducir consultas a base de datos.
Utiliza caché manual basado en IDs de productos y objetos.
"""
from typing import Dict, Any, Optional, List
from sqlmodel import Session, select
import json

# ==================== CACHÉS MANUALES ====================
_cache_especialidades: Dict[int, str] = {}
_cache_tamaños_pizzas: Dict[int, str] = {}
_cache_pizzas: Dict[int, Dict[str, Any]] = {}
_cache_hamburguesas: Dict[int, Dict[str, Any]] = {}
_cache_costillas: Dict[int, Dict[str, Any]] = {}
_cache_alitas: Dict[int, Dict[str, Any]] = {}
_cache_spaghetti: Dict[int, Dict[str, Any]] = {}
_cache_papas: Dict[int, Dict[str, Any]] = {}
_cache_mariscos: Dict[int, Dict[str, Any]] = {}
_cache_refrescos: Dict[int, Dict[str, Any]] = {}
_cache_magno: Dict[int, Dict[str, Any]] = {}
_cache_rectangular: Dict[int, Dict[str, Any]] = {}
_cache_barra: Dict[int, Dict[str, Any]] = {}


# ==================== FUNCIONES DE CACHÉ PARA LOOKUPS ====================

def get_especialidad_nombre(session: Session, id_esp: int) -> str:
    """Obtiene el nombre de una especialidad con caché."""
    if id_esp not in _cache_especialidades:
        from app.models.especialidadModel import especialidad
        esp = session.get(especialidad, id_esp)
        _cache_especialidades[id_esp] = esp.nombre if esp else f"Especialidad #{id_esp}"
    return _cache_especialidades[id_esp]


def get_tamano_pizza_nombre(session: Session, id_tamano: int) -> str:
    """Obtiene el nombre de un tamaño de pizza con caché."""
    if id_tamano not in _cache_tamaños_pizzas:
        from app.models.tamanosPizzasModel import tamanosPizzas
        tamano_obj = session.get(tamanosPizzas, id_tamano)
        _cache_tamaños_pizzas[id_tamano] = tamano_obj.tamano if tamano_obj else f"Tamaño #{id_tamano}"
    return _cache_tamaños_pizzas[id_tamano]


# ==================== FUNCIONES CACHEADAS DE PROCESAMIENTO ====================

def procesar_producto_personalizado_cached(
    session: Session, 
    det_cantidad: int,
    det_ingredientes: Dict[str, Any],
    det_status: str
) -> Dict[str, Any]:
    """Procesar productos personalizados con ingredientes - versión cacheada."""
    from app.models.ventaModel import Ingredientes
    from app.models.tamanosPizzasModel import tamanosPizzas
    
    try:
        ingredientes_data = det_ingredientes
        tamano_id = ingredientes_data.get("tamano")
        ids_ingredientes = ingredientes_data.get("ingredientes", [])
        
        # Obtener el nombre del tamaño (con caché)
        nombre_tamano = get_tamano_pizza_nombre(session, tamano_id)
        
        # Obtener nombres de los ingredientes
        nombres_ingredientes = []
        for id_ing in ids_ingredientes:
            ingrediente = session.get(Ingredientes, id_ing)
            if ingrediente:
                nombres_ingredientes.append(ingrediente.ingrediente)
            else:
                nombres_ingredientes.append(f"Ingrediente #{id_ing}")
        
        return {
            "cantidad": det_cantidad,
            "nombre": f"Pizza Personalizada - {nombre_tamano}",
            "tipo": "Pizza Personalizada",
            "status": det_status,
            "es_personalizado": True,
            "tamano": nombre_tamano,
            "detalles_ingredientes": {
                "tamano": nombre_tamano,
                "tamano_id": tamano_id,
                "ingredientes": nombres_ingredientes,
                "cantidad_ingredientes": len(nombres_ingredientes)
            }
        }
    except Exception as e:
        return {
            "cantidad": det_cantidad,
            "nombre": "Pizza Personalizada - Error al cargar",
            "tipo": "Pizza Personalizada",
            "status": det_status,
            "es_personalizado": True,
            "tamano": "Error",
            "detalles_ingredientes": {"error": str(e)}
        }


def procesar_pizza_cached(session: Session, det_cantidad: int, id_pizza: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar pizza con caché."""
    if id_pizza not in _cache_pizzas:
        from app.models.pizzasModel import pizzas
        
        producto = session.get(pizzas, id_pizza)
        if not producto:
            _cache_pizzas[id_pizza] = None
            return None
        
        try:
            nombre_especialidad = get_especialidad_nombre(session, producto.id_esp)
            nombre_tamano = get_tamano_pizza_nombre(session, producto.id_tamano)
        except:
            nombre_especialidad = f"Especialidad #{producto.id_esp}"
            nombre_tamano = f"Tamaño #{producto.id_tamano}"
        
        _cache_pizzas[id_pizza] = {
            "nombre": f"{nombre_especialidad} - {nombre_tamano}",
            "tamano": nombre_tamano,
            "especialidad": nombre_especialidad
        }
    
    if _cache_pizzas[id_pizza] is None:
        return None
    
    cached = _cache_pizzas[id_pizza]
    return {
        "cantidad": det_cantidad,
        "nombre": cached["nombre"],
        "tipo": "Pizza",
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": cached["tamano"]
    }


def procesar_hamburguesa_cached(session: Session, det_cantidad: int, id_hamb: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar hamburguesa con caché."""
    if id_hamb not in _cache_hamburguesas:
        from app.models.hamburguesasModel import hamburguesas
        
        producto = session.get(hamburguesas, id_hamb)
        if not producto:
            _cache_hamburguesas[id_hamb] = None
            return None
        
        _cache_hamburguesas[id_hamb] = {"nombre": producto.paquete}
    
    if _cache_hamburguesas[id_hamb] is None:
        return None
    
    cached = _cache_hamburguesas[id_hamb]
    return {
        "cantidad": det_cantidad,
        "nombre": cached["nombre"],
        "tipo": "Hamburguesa",
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_costilla_cached(session: Session, det_cantidad: int, id_cos: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar costilla con caché."""
    if id_cos not in _cache_costillas:
        from app.models.costillasModel import costillas
        
        producto = session.get(costillas, id_cos)
        if not producto:
            _cache_costillas[id_cos] = None
            return None
        
        _cache_costillas[id_cos] = {"nombre": producto.orden}
    
    if _cache_costillas[id_cos] is None:
        return None
    
    cached = _cache_costillas[id_cos]
    return {
        "cantidad": det_cantidad,
        "nombre": cached["nombre"],
        "tipo": "Costilla",
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_alitas_cached(session: Session, det_cantidad: int, id_alis: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar alitas con caché."""
    if id_alis not in _cache_alitas:
        from app.models.alitasModel import alitas
        
        producto = session.get(alitas, id_alis)
        if not producto:
            _cache_alitas[id_alis] = None
            return None
        
        _cache_alitas[id_alis] = {"nombre": producto.orden}
    
    if _cache_alitas[id_alis] is None:
        return None
    
    cached = _cache_alitas[id_alis]
    return {
        "cantidad": det_cantidad,
        "nombre": cached["nombre"],
        "tipo": "Alitas",
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_spaghetti_cached(session: Session, det_cantidad: int, id_spag: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar spaghetti con caché."""
    if id_spag not in _cache_spaghetti:
        from app.models.spaguettyModel import spaguetty
        
        producto = session.get(spaguetty, id_spag)
        if not producto:
            _cache_spaghetti[id_spag] = None
            return None
        
        _cache_spaghetti[id_spag] = {"nombre": producto.orden}
    
    if _cache_spaghetti[id_spag] is None:
        return None
    
    cached = _cache_spaghetti[id_spag]
    return {
        "cantidad": det_cantidad,
        "nombre": cached["nombre"],
        "tipo": "Spaghetti",
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_papas_cached(session: Session, det_cantidad: int, id_papa: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar papas con caché."""
    if id_papa not in _cache_papas:
        from app.models.papasModel import papas
        
        producto = session.get(papas, id_papa)
        if not producto:
            _cache_papas[id_papa] = None
            return None
        
        _cache_papas[id_papa] = {"nombre": producto.orden}
    
    if _cache_papas[id_papa] is None:
        return None
    
    cached = _cache_papas[id_papa]
    return {
        "cantidad": det_cantidad,
        "nombre": cached["nombre"],
        "tipo": "Papas",
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_mariscos_cached(session: Session, det_cantidad: int, id_maris: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar mariscos con caché."""
    if id_maris not in _cache_mariscos:
        from app.models.mariscosModel import mariscos
        from app.models.tamanosPizzasModel import tamanosPizzas
        
        producto = session.get(mariscos, id_maris)
        if not producto:
            _cache_mariscos[id_maris] = None
            return None
        
        try:
            tamano_obj = session.get(tamanosPizzas, producto.id_tamañop) if hasattr(producto, 'id_tamañop') else None
            tamano_marisco = tamano_obj.tamano if tamano_obj else "Tamaño desconocido"
            nombre_producto = f"{producto.nombre} - {tamano_marisco}"
        except:
            nombre_producto = producto.nombre
            tamano_marisco = "Tamaño desconocido"
        
        _cache_mariscos[id_maris] = {"nombre": nombre_producto, "tamano": tamano_marisco}
    
    if _cache_mariscos[id_maris] is None:
        return None
    
    cached = _cache_mariscos[id_maris]
    return {
        "cantidad": det_cantidad,
        "nombre": cached["nombre"],
        "tipo": "Mariscos",
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": cached["tamano"]
    }


def procesar_refresco_cached(session: Session, det_cantidad: int, id_refresco: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar refresco con caché."""
    if id_refresco not in _cache_refrescos:
        from app.models.refrescosModel import refrescos
        
        producto = session.get(refrescos, id_refresco)
        if not producto:
            _cache_refrescos[id_refresco] = None
            return None
        
        _cache_refrescos[id_refresco] = {"nombre": producto.nombre}
    
    if _cache_refrescos[id_refresco] is None:
        return None
    
    cached = _cache_refrescos[id_refresco]
    return {
        "cantidad": det_cantidad,
        "nombre": cached["nombre"],
        "tipo": "Refresco",
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_magno_cached(session: Session, det_cantidad: int, id_magno_data: Any, det_status: str) -> List[Dict[str, Any]]:
    """Procesar magno con caché."""
    from app.models.magnoModel import magno
    from app.models.especialidadModel import especialidad
    
    try:
        lista_ids = json.loads(id_magno_data) if isinstance(id_magno_data, str) else id_magno_data
    except:
        lista_ids = id_magno_data if isinstance(id_magno_data, list) else [id_magno_data]
    
    nombres_magno = []
    for id_mag in lista_ids:
        if id_mag not in _cache_magno:
            producto = session.get(magno, id_mag)
            if producto:
                try:
                    nombre_especialidad = get_especialidad_nombre(session, producto.id_especialidad)
                except:
                    nombre_especialidad = f"Especialidad #{producto.id_especialidad}"
                _cache_magno[id_mag] = {"especialidad": nombre_especialidad}
            else:
                _cache_magno[id_mag] = None
        
        if _cache_magno[id_mag]:
            nombres_magno.append(_cache_magno[id_mag]["especialidad"])
    
    if nombres_magno:
        return [{
            "cantidad": det_cantidad,
            "nombre": "Magno",
            "tipo": "Magno",
            "especialidades": nombres_magno,
            "status": det_status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    return []


def procesar_rectangular_cached(session: Session, det_cantidad: int, id_rec_data: Any, det_status: str) -> List[Dict[str, Any]]:
    """Procesar rectangular con caché."""
    from app.models.rectangularModel import rectangular
    from app.models.especialidadModel import especialidad
    
    try:
        lista_ids = json.loads(id_rec_data) if isinstance(id_rec_data, str) else id_rec_data
    except:
        lista_ids = id_rec_data if isinstance(id_rec_data, list) else [id_rec_data]
    
    nombres_rect = []
    for id_rec in lista_ids:
        if id_rec not in _cache_rectangular:
            producto = session.get(rectangular, id_rec)
            if producto:
                try:
                    nombre_especialidad = get_especialidad_nombre(session, producto.id_esp)
                except:
                    nombre_especialidad = f"Especialidad #{producto.id_esp}"
                _cache_rectangular[id_rec] = {"especialidad": nombre_especialidad}
            else:
                _cache_rectangular[id_rec] = None
        
        if _cache_rectangular[id_rec]:
            nombres_rect.append(_cache_rectangular[id_rec]["especialidad"])
    
    if nombres_rect:
        return [{
            "cantidad": det_cantidad,
            "nombre": "Rectangular",
            "tipo": "Rectangular",
            "especialidades": nombres_rect,
            "status": det_status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    return []


def procesar_barra_cached(session: Session, det_cantidad: int, id_barr_data: Any, det_status: str) -> List[Dict[str, Any]]:
    """Procesar barra con caché."""
    from app.models.barraModel import barra
    from app.models.especialidadModel import especialidad
    
    try:
        lista_ids = json.loads(id_barr_data) if isinstance(id_barr_data, str) else id_barr_data
    except:
        lista_ids = id_barr_data if isinstance(id_barr_data, list) else [id_barr_data]
    
    nombres_barr = []
    for id_barr in lista_ids:
        if id_barr not in _cache_barra:
            producto = session.get(barra, id_barr)
            if producto:
                try:
                    nombre_especialidad = get_especialidad_nombre(session, producto.id_especialidad)
                except:
                    nombre_especialidad = f"Especialidad #{producto.id_especialidad}"
                _cache_barra[id_barr] = {"especialidad": nombre_especialidad}
            else:
                _cache_barra[id_barr] = None
        
        if _cache_barra[id_barr]:
            nombres_barr.append(_cache_barra[id_barr]["especialidad"])
    
    if nombres_barr:
        return [{
            "cantidad": det_cantidad,
            "nombre": "Barra",
            "tipo": "Barra",
            "especialidades": nombres_barr,
            "status": det_status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    return []


def procesar_paquetes_tipo_1_3_cached(session: Session, det_cantidad: int, id_paquete: int, detalle_paquete: str, det_status: str) -> List[Dict[str, Any]]:
    """Procesar paquetes tipo 1 y 3 con caché."""
    from app.models.pizzasModel import pizzas
    from app.models.especialidadModel import especialidad
    
    productos = []
    if detalle_paquete:
        ids_pizzas = detalle_paquete.split(",")
        
        for id_pizza_str in ids_pizzas:
            try:
                id_pizza = int(id_pizza_str.strip())
                
                # Usar función cacheada para pizza
                pizza_result = procesar_pizza_cached(session, 1, id_pizza, det_status)
                if pizza_result:
                    pizza_result["tipo"] = f"Paquete {id_paquete} - Pizza"
                    productos.append(pizza_result)
                else:
                    productos.append({
                        "cantidad": 1,
                        "nombre": f"Error al cargar pizza #{id_pizza}",
                        "tipo": f"Paquete {id_paquete}",
                        "status": det_status,
                        "es_personalizado": False,
                        "detalles_ingredientes": None,
                        "tamano": None
                    })
            
            except (ValueError, AttributeError) as e:
                productos.append({
                    "cantidad": 1,
                    "nombre": f"Error al cargar pizza del paquete",
                    "tipo": f"Paquete {id_paquete}",
                    "status": det_status,
                    "es_personalizado": False,
                    "detalles_ingredientes": None,
                    "tamano": None
                })
    else:
        productos.append({
            "cantidad": det_cantidad,
            "nombre": f"Paquete {id_paquete} - Sin detalle",
            "tipo": "Paquete",
            "status": det_status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        })
    
    return productos


def procesar_paquetes_tipo_2_cached(session: Session, det_cantidad: int, id_paquete: int, id_refresco: Optional[int], id_pizza: Optional[int], id_alis: Optional[int], id_hamb: Optional[int], det_status: str) -> List[Dict[str, Any]]:
    """Procesar paquete tipo 2 con caché."""
    productos = []
    
    # Refresco
    if id_refresco:
        refresco_result = procesar_refresco_cached(session, 1, id_refresco, det_status)
        if refresco_result:
            refresco_result["tipo"] = f"Paquete {id_paquete} - Refresco"
            productos.append(refresco_result)
    
    # Pizza
    if id_pizza:
        pizza_result = procesar_pizza_cached(session, 1, id_pizza, det_status)
        if pizza_result:
            pizza_result["tipo"] = f"Paquete {id_paquete} - Pizza"
            productos.append(pizza_result)
    
    # Alitas o Hamburguesa
    if id_alis:
        alita_result = procesar_alitas_cached(session, 1, id_alis, det_status)
        if alita_result:
            alita_result["tipo"] = f"Paquete {id_paquete} - Alitas"
            productos.append(alita_result)
    elif id_hamb:
        hamb_result = procesar_hamburguesa_cached(session, 1, id_hamb, det_status)
        if hamb_result:
            hamb_result["tipo"] = f"Paquete {id_paquete} - Hamburguesa"
            productos.append(hamb_result)
    
    return productos


def clear_all_caches():
    """Limpia todos los cachés. Útil para testing o invalidación forzada."""
    global _cache_especialidades, _cache_tamaños_pizzas, _cache_pizzas
    global _cache_hamburguesas, _cache_costillas, _cache_alitas, _cache_spaghetti
    global _cache_papas, _cache_mariscos, _cache_refrescos, _cache_magno
    global _cache_rectangular, _cache_barra
    
    _cache_especialidades.clear()
    _cache_tamaños_pizzas.clear()
    _cache_pizzas.clear()
    _cache_hamburguesas.clear()
    _cache_costillas.clear()
    _cache_alitas.clear()
    _cache_spaghetti.clear()
    _cache_papas.clear()
    _cache_mariscos.clear()
    _cache_refrescos.clear()
    _cache_magno.clear()
    _cache_rectangular.clear()
    _cache_barra.clear()
