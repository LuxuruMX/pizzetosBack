"""
Módulo de funciones cacheadas para reducir consultas a base de datos.
Utiliza caché manual basado en IDs de productos y objetos con TTL de 5 días.
Thread-safe para FastAPI async.
"""
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from sqlmodel import Session, select
import json
from datetime import datetime, timedelta

# Importar Lock para thread safety
from threading import Lock

# ==================== ESTRUCTURA DE CACHÉ CON TTL Y THREAD SAFETY ====================
class TTLCache:
    def __init__(self, ttl_days: int = 5):
        self.cache: Dict[Any, Tuple[Any, datetime]] = {}
        self.ttl = timedelta(days=ttl_days)
        self._lock = Lock()  # Lock para thread safety
    
    def get(self, key: Any) -> Optional[Any]:
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if datetime.now() - timestamp < self.ttl:
                    return value
                else:
                    # Eliminar entrada expirada
                    del self.cache[key]
            return None
    
    def set(self, key: Any, value: Any):
        with self._lock:
            self.cache[key] = (value, datetime.now())
    
    def clear(self):
        with self._lock:
            self.cache.clear()
    
    def cleanup_expired(self):
        """Eliminar entradas expiradas manualmente si es necesario"""
        with self._lock:
            expired_keys = []
            now = datetime.now()
            for key, (value, timestamp) in self.cache.items():
                if now - timestamp >= self.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]

# ==================== INSTANCIAS DE CACHÉ CON TTL ====================
_cache_especialidades = TTLCache(ttl_days=5)
_cache_tamaños_pizzas = TTLCache(ttl_days=5)
_cache_pizzas = TTLCache(ttl_days=5)
_cache_hamburguesas = TTLCache(ttl_days=5)
_cache_costillas = TTLCache(ttl_days=5)
_cache_alitas = TTLCache(ttl_days=5)
_cache_spaghetti = TTLCache(ttl_days=5)
_cache_papas = TTLCache(ttl_days=5)
_cache_mariscos = TTLCache(ttl_days=5)
_cache_refrescos = TTLCache(ttl_days=5)
_cache_magno = TTLCache(ttl_days=5)
_cache_rectangular = TTLCache(ttl_days=5)
_cache_barra = TTLCache(ttl_days=5)


# ==================== FUNCIONES DE CACHÉ PARA LOOKUPS ====================

def get_especialidad_nombre(session: Session, id_esp: int) -> str:
    """Obtiene el nombre de una especialidad con caché y TTL."""
    cached_value = _cache_especialidades.get(id_esp)
    if cached_value is not None:
        return cached_value
    
    from app.models.especialidadModel import especialidad
    esp = session.get(especialidad, id_esp)
    result = esp.nombre if esp else f"Especialidad #{id_esp}"
    _cache_especialidades.set(id_esp, result)
    return result


def get_tamano_pizza_nombre(session: Session, id_tamano: int) -> str:
    """Obtiene el nombre de un tamaño de pizza con caché y TTL."""
    cached_value = _cache_tamaños_pizzas.get(id_tamano)
    if cached_value is not None:
        return cached_value
    
    from app.models.tamanosPizzasModel import tamanosPizzas
    tamano_obj = session.get(tamanosPizzas, id_tamano)
    result = tamano_obj.tamano.replace(" Especial", "").replace(" Camaron", "").replace(" Mar", "") if tamano_obj else f"Tamaño #{id_tamano}"
    _cache_tamaños_pizzas.set(id_tamano, result)
    return result


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
    """Procesar pizza con caché y TTL."""
    # Creamos una clave compuesta para incluir la cantidad y el status
    cache_key = (id_pizza, det_cantidad, det_status)
    cached_value = _cache_pizzas.get(cache_key)
    if cached_value is not None:
        if cached_value is None:  # Caso especial para productos no encontrados
            return None
        # Devolvemos una copia para evitar modificaciones accidentales
        cached = cached_value.copy()
        cached.update({
            "cantidad": det_cantidad,
            "status": det_status,
            "tipo": "Pizza"
            
        })
        return cached
    
    from app.models.pizzasModel import pizzas
    
    producto = session.get(pizzas, id_pizza)
    if not producto:
        _cache_pizzas.set(cache_key, None)
        return None
    
    try:
        nombre_especialidad = get_especialidad_nombre(session, producto.id_esp)
        nombre_tamano = get_tamano_pizza_nombre(session, producto.id_tamano)
    except:
        nombre_especialidad = f"Especialidad #{producto.id_esp}"
        nombre_tamano = f"Tamaño #{producto.id_tamano}"
    
    result = {
        "nombre": f"{nombre_especialidad} - {nombre_tamano}",
        "especialidad": nombre_especialidad
    }
    
    _cache_pizzas.set(cache_key, result)
    
    return {
        "cantidad": det_cantidad,
        "nombre": result["nombre"],
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
    }


def procesar_hamburguesa_cached(session: Session, det_cantidad: int, id_hamb: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar hamburguesa con caché y TTL."""
    cache_key = (id_hamb, det_cantidad, det_status)
    cached_value = _cache_hamburguesas.get(cache_key)
    if cached_value is not None:
        if cached_value is None:
            return None
        cached = cached_value.copy()
        cached.update({
            "cantidad": det_cantidad,
            "status": det_status,
            "tipo": "Hamburguesa"
        })
        return cached
    
    from app.models.hamburguesasModel import hamburguesas
    
    producto = session.get(hamburguesas, id_hamb)
    if not producto:
        _cache_hamburguesas.set(cache_key, None)
        return None
    
    result = {"nombre": producto.paquete}
    _cache_hamburguesas.set(cache_key, result)
    
    return {
        "cantidad": det_cantidad,
        "nombre": result["nombre"],
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_costilla_cached(session: Session, det_cantidad: int, id_cos: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar costilla con caché y TTL."""
    cache_key = (id_cos, det_cantidad, det_status)
    cached_value = _cache_costillas.get(cache_key)
    if cached_value is not None:
        if cached_value is None:
            return None
        cached = cached_value.copy()
        cached.update({
            "cantidad": det_cantidad,
            "status": det_status,
            "tipo": "Costillas"
        })
        return cached
    
    from app.models.costillasModel import costillas
    
    producto = session.get(costillas, id_cos)
    if not producto:
        _cache_costillas.set(cache_key, None)
        return None
    
    result = {"nombre": producto.orden}
    _cache_costillas.set(cache_key, result)
    
    return {
        "cantidad": det_cantidad,
        "nombre": result["nombre"],
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_alitas_cached(session: Session, det_cantidad: int, id_alis: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar alitas con caché y TTL."""
    cache_key = (id_alis, det_cantidad, det_status)
    cached_value = _cache_alitas.get(cache_key)
    if cached_value is not None:
        if cached_value is None:
            return None
        cached = cached_value.copy()
        cached.update({
            "cantidad": det_cantidad,
            "status": det_status,
            "tipo": "Alitas"
        })
        return cached
    
    from app.models.alitasModel import alitas
    
    producto = session.get(alitas, id_alis)
    if not producto:
        _cache_alitas.set(cache_key, None)
        return None
    
    result = {"nombre": producto.orden}
    _cache_alitas.set(cache_key, result)
    
    return {
        "cantidad": det_cantidad,
        "nombre": result["nombre"],
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_spaghetti_cached(session: Session, det_cantidad: int, id_spag: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar spaghetti con caché y TTL."""
    cache_key = (id_spag, det_cantidad, det_status)
    cached_value = _cache_spaghetti.get(cache_key)
    if cached_value is not None:
        if cached_value is None:
            return None
        cached = cached_value.copy()
        cached.update({
            "cantidad": det_cantidad,
            "status": det_status,
            "tipo": "Spaghetti"
        })
        return cached
    
    from app.models.spaguettyModel import spaguetty
    
    producto = session.get(spaguetty, id_spag)
    if not producto:
        _cache_spaghetti.set(cache_key, None)
        return None
    
    result = {"nombre": producto.orden}
    _cache_spaghetti.set(cache_key, result)
    
    return {
        "cantidad": det_cantidad,
        "nombre": result["nombre"],
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_papas_cached(session: Session, det_cantidad: int, id_papa: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar papas con caché y TTL."""
    cache_key = (id_papa, det_cantidad, det_status)
    cached_value = _cache_papas.get(cache_key)
    if cached_value is not None:
        if cached_value is None:
            return None
        cached = cached_value.copy()
        cached.update({
            "cantidad": det_cantidad,
            "status": det_status,
            "tipo": "Papas"
        })
        return cached
    
    from app.models.papasModel import papas
    
    producto = session.get(papas, id_papa)
    if not producto:
        _cache_papas.set(cache_key, None)
        return None
    
    result = {"nombre": producto.orden}
    _cache_papas.set(cache_key, result)
    
    return {
        "cantidad": det_cantidad,
        "nombre": result["nombre"],
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_mariscos_cached(session: Session, det_cantidad: int, id_maris: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar mariscos con caché y TTL."""
    cache_key = (id_maris, det_cantidad, det_status)
    cached_value = _cache_mariscos.get(cache_key)
    if cached_value is not None:
        if cached_value is None:
            return None
        cached = cached_value.copy()
        cached.update({
            "cantidad": det_cantidad,
            "status": det_status,
            "tipo": "Mariscos"
        })
        return cached
    
    from app.models.mariscosModel import mariscos
    from app.models.tamanosPizzasModel import tamanosPizzas
    
    producto = session.get(mariscos, id_maris)
    if not producto:
        _cache_mariscos.set(cache_key, None)
        return None
    
    try:
        tamano_obj = session.get(tamanosPizzas, producto.id_tamañop) if hasattr(producto, 'id_tamañop') else None
        tamano_marisco = tamano_obj.tamano if tamano_obj else "Tamaño desconocido"
        nombre_producto = f"{producto.nombre} - {tamano_marisco}"
    except:
        nombre_producto = producto.nombre
        tamano_marisco = "Tamaño desconocido"
    
    result = {"nombre": nombre_producto, "tamano": tamano_marisco}
    _cache_mariscos.set(cache_key, result)
    
    return {
        "cantidad": det_cantidad,
        "nombre": result["nombre"],
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": result["tamano"]
    }


def procesar_refresco_cached(session: Session, det_cantidad: int, id_refresco: int, det_status: str) -> Optional[Dict[str, Any]]:
    """Procesar refresco con caché y TTL."""
    cache_key = (id_refresco, det_cantidad, det_status)
    cached_value = _cache_refrescos.get(cache_key)
    if cached_value is not None:
        if cached_value is None:
            return None
        cached = cached_value.copy()
        cached.update({
            "cantidad": det_cantidad,
            "status": det_status,
            "tipo": "Refresco"
        })
        return cached
    
    from app.models.refrescosModel import refrescos
    
    producto = session.get(refrescos, id_refresco)
    if not producto:
        _cache_refrescos.set(cache_key, None)
        return None
    
    result = {"nombre": producto.nombre}
    _cache_refrescos.set(cache_key, result)
    
    return {
        "cantidad": det_cantidad,
        "nombre": result["nombre"],
        "status": det_status,
        "es_personalizado": False,
        "detalles_ingredientes": None,
        "tamano": None
    }


def procesar_magno_cached(session: Session, det_cantidad: int, id_magno_data: Any, det_status: str) -> List[Dict[str, Any]]:

    from app.models.magnoModel import magno
    
    try:
        lista_ids = json.loads(id_magno_data) if isinstance(id_magno_data, str) else id_magno_data
    except:
        lista_ids = id_magno_data if isinstance(id_magno_data, list) else [id_magno_data]
    
    cache_key = (tuple(sorted(lista_ids)) if isinstance(lista_ids, list) else id_magno_data, det_cantidad, det_status)
    cached_value = _cache_magno.get(cache_key)
    if cached_value is not None:
        result = []
        for item in cached_value:
            new_item = item.copy()
            new_item.update({
                "cantidad": det_cantidad,
                "status": det_status,
                "tipo": "Magno"
            })
            result.append(new_item)
        return result
    
    nombres_magno = []
    for id_mag in lista_ids:
        producto = session.get(magno, id_mag)
        if producto:
            try:
                nombre_especialidad = get_especialidad_nombre(session, producto.id_especialidad)
            except:
                nombre_especialidad = f"Especialidad #{producto.id_especialidad}"
            nombres_magno.append(nombre_especialidad)
    
    result = []
    if nombres_magno:
        result = [{
            "cantidad": det_cantidad,
            "nombre": "Magno",
            "especialidades": nombres_magno,
            "status": det_status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    
    _cache_magno.set(cache_key, result)
    return result


def procesar_rectangular_cached(session: Session, det_cantidad: int, id_rec_data: Any, det_status: str) -> List[Dict[str, Any]]:
    """Procesar rectangular con caché y TTL."""
    from app.models.rectangularModel import rectangular
    
    try:
        lista_ids = json.loads(id_rec_data) if isinstance(id_rec_data, str) else id_rec_data
    except:
        lista_ids = id_rec_data if isinstance(id_rec_data, list) else [id_rec_data]
    
    cache_key = (tuple(sorted(lista_ids)) if isinstance(lista_ids, list) else id_rec_data, det_cantidad, det_status)
    cached_value = _cache_rectangular.get(cache_key)
    if cached_value is not None:
        result = []
        for item in cached_value:
            new_item = item.copy()
            new_item.update({
                "cantidad": det_cantidad,
                "status": det_status,
                "tipo": "Rectangular"
            })
            result.append(new_item)
        return result
    
    nombres_rect = []
    for id_rec in lista_ids:
        producto = session.get(rectangular, id_rec)
        if producto:
            try:
                nombre_especialidad = get_especialidad_nombre(session, producto.id_esp)
            except:
                nombre_especialidad = f"Especialidad #{producto.id_esp}"
            nombres_rect.append(nombre_especialidad)
    
    result = []
    if nombres_rect:
        result = [{
            "cantidad": det_cantidad,
            "nombre": "Rectangular",
            "especialidades": nombres_rect,
            "status": det_status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    
    _cache_rectangular.set(cache_key, result)
    return result


def procesar_barra_cached(session: Session, det_cantidad: int, id_barr_data: Any, det_status: str) -> List[Dict[str, Any]]:
    """Procesar barra con caché y TTL."""
    from app.models.barraModel import barra
    
    try:
        lista_ids = json.loads(id_barr_data) if isinstance(id_barr_data, str) else id_barr_data
    except:
        lista_ids = id_barr_data if isinstance(id_barr_data, list) else [id_barr_data]
    
    cache_key = (tuple(sorted(lista_ids)) if isinstance(lista_ids, list) else id_barr_data, det_cantidad, det_status)
    cached_value = _cache_barra.get(cache_key)
    if cached_value is not None:
        result = []
        for item in cached_value:
            new_item = item.copy()
            new_item.update({
                "cantidad": det_cantidad,
                "status": det_status,
                "tipo": "Barra"
            })
            result.append(new_item)
        return result
    
    nombres_barr = []
    for id_barr in lista_ids:
        producto = session.get(barra, id_barr)
        if producto:
            try:
                nombre_especialidad = get_especialidad_nombre(session, producto.id_especialidad)
            except:
                nombre_especialidad = f"Especialidad #{producto.id_especialidad}"
            nombres_barr.append(nombre_especialidad)
    
    result = []
    if nombres_barr:
        result = [{
            "cantidad": det_cantidad,
            "nombre": "Barra",
            "especialidades": nombres_barr,
            "status": det_status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        }]
    
    _cache_barra.set(cache_key, result)
    return result


def procesar_paquetes_tipo_1_3_cached(session: Session, det_cantidad: int, id_paquete: int, detalle_paquete: str, det_status: str) -> List[Dict[str, Any]]:
    """Procesar paquetes tipo 1 y 3 con caché y TTL."""
    cache_key = (id_paquete, detalle_paquete, det_cantidad, det_status)
    cached_value = _cache_pizzas.get(cache_key)  # Reutilizamos el caché temporalmente
    if cached_value is not None:
        result = []
        for item in cached_value:
            new_item = item.copy()
            new_item.update({
                "cantidad": det_cantidad,
                "status": det_status,
                "tipo": f"Paquete {id_paquete}"
            })
            result.append(new_item)
        return result
    
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
                        "status": det_status,
                        "es_personalizado": False,
                        "detalles_ingredientes": None,
                        "tamano": None
                    })
            
            except (ValueError, AttributeError) as e:
                productos.append({
                    "cantidad": 1,
                    "nombre": f"Error al cargar pizza del paquete",
                    "status": det_status,
                    "es_personalizado": False,
                    "detalles_ingredientes": None,
                    "tamano": None
                })
    else:
        productos.append({
            "cantidad": det_cantidad,
            "nombre": f"Paquete {id_paquete} - Sin detalle",
            "status": det_status,
            "es_personalizado": False,
            "detalles_ingredientes": None,
            "tamano": None
        })
    
    # Guardar en caché la combinación completa
    _cache_pizzas.set(cache_key, productos)
    return productos


def procesar_paquetes_tipo_2_cached(session: Session, det_cantidad: int, id_paquete: int, id_refresco: Optional[int], id_pizza: Optional[int], id_alis: Optional[int], id_hamb: Optional[int], det_status: str) -> List[Dict[str, Any]]:
    """Procesar paquete tipo 2 con caché y TTL."""
    cache_key = (id_paquete, id_refresco, id_pizza, id_alis, id_hamb, det_cantidad, det_status)
    temp_cache = TTLCache(ttl_days=5)
    cached_value = temp_cache.get(cache_key)
    if cached_value is not None:
        result = []
        for item in cached_value:
            new_item = item.copy()
            new_item.update({
                "cantidad": det_cantidad,
                "status": det_status,
                "tipo": f"Paquete {id_paquete}"
            })
            result.append(new_item)
        return result
    
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
    
    temp_cache.set(cache_key, productos)
    return productos


def clear_all_caches():
    """Limpia todos los cachés. Útil para testing o invalidación forzada."""
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


def cleanup_expired_caches():
    """Limpiar manualmente todas las entradas expiradas"""
    for cache in [
        _cache_especialidades, _cache_tamaños_pizzas, _cache_pizzas,
        _cache_hamburguesas, _cache_costillas, _cache_alitas, _cache_spaghetti,
        _cache_papas, _cache_mariscos, _cache_refrescos, _cache_magno,
        _cache_rectangular, _cache_barra
    ]:
        cache.cleanup_expired()



def _construir_productos_desde_cache(
    info_paquete: Dict[str, Any],
    cantidad_detalle: int,
    status_detalle: str
) -> List[Dict[str, Any]]:
    """Construye la lista de productos a partir de la info cacheada, ajustando cantidad y status."""
    productos = []
    for prod in info_paquete.get('productos', []):
        # Hacemos una copia para no alterar el objeto cacheado
        item = prod.copy()
        # Ajustamos cantidad y status con los del detalle actual
        item['cantidad'] = cantidad_detalle * item.get('cantidad', 1)
        item['status'] = status_detalle
        productos.append(item)
    return productos