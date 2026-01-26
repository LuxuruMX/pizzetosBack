"""
Ejemplo de cómo usar el endpoint GET /recrea-ticket/{id_venta}

El endpoint retorna la información de un ticket formateada similar a /pedidos-cocina,
pero incluyendo campos adicionales para recrear el ticket en frontend:
- precio_base: Precio sin extras
- precio_extra: Costo total de extras
- precioUnitario: Precio total
- conQueso: Si tiene queso
- id_paquete, id_rec, id_barr: IDs de productos especiales
"""

# EJEMPLO DE RESPUESTA para un ticket con múltiples productos:
ejemplo_respuesta = {
    "id_venta": 123,
    "fecha_hora": "2026-01-26T14:30:00",
    "cliente": "Juan Pérez",
    "tipo_servicio": 0,
    "tipo_servicio_texto": "Comer aquí",
    "mesa": 5,
    "sucursal": "Sucursal Centro",
    "status": 1,
    "comentarios": "Sin cebolla",
    "status_texto": "Preparando",
    "cantidad_items": 4,
    "cantidad_productos_diferentes": 3,
    "total_venta": 650.0,
    "productos": [
        {
            "nombre": "Hawaiana",
            "tamano": "Mediana",
            "cantidad": 2,
            "tipo": "Pizza",
            "precio_base": 255.0,
            "precio_extra": 40.0,
            "precioUnitario": 295.0,
            "conQueso": True,
            "precioUnitario": 295.0,
            "con_queso": True,
        },
        {
            "nombre": "Alitas BBQ",
            "tamano": "Media",
            "cantidad": 1,
            "tipo": "Alitas",
            "precio_base": 150.0,
            "precio_extra": 0.0,
            "precioUnitario": 150.0,
            "conQueso": False,
        },
        {
            "nombre": "Coca Cola",
            "tamano": "2L",
            "cantidad": 1,
            "tipo": "Refresco",
            "precio_base": 55.0,
            "precio_extra": 0.0,
            "precioUnitario": 55.0,
            "conQueso": False,
        }
    ]
}

# USO:
# curl -X GET "http://localhost:8000/recrea-ticket/123"
# 
# Retorna la información del ticket 123 en el formato anterior,
# con todos los datos necesarios para recrear el ticket en frontend.

# El endpoint utiliza la misma lógica que /pedidos-cocina pero enriquecida
# con los campos precio_base, precio_extra, permitiendo que el frontend
# recree exactamente el ticket como se vendió originalmente.

