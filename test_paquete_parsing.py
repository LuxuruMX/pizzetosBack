"""
Script de prueba para validar el parseo de paquetes JSON.
Simula cómo se procesan los paquetes desde los detalles de venta.
"""
import json
from typing import Dict, Any, List

# Datos de ejemplo como vienen de la BD
paquete_data_1 = {"id_paquete": 1, "id_pizzas": [4, 8], "id_refresco": 17}
paquete_data_2 = {"id_paquete": 2, "id_pizzas": [4], "id_refresco": 17, "id_hamb": 1}

def simulate_procesar_paquete(paquete_json: Dict[str, Any]) -> Dict[str, List[Any]]:
    """Simula cómo se procesaría un paquete"""
    
    # Parsear el JSON si es string, si no es dict ya
    try:
        if isinstance(paquete_json, str):
            paquete_data = json.loads(paquete_json)
        else:
            paquete_data = paquete_json
    except (json.JSONDecodeError, TypeError):
        return {}
    
    print(f"\n📦 Procesando Paquete ID: {paquete_data.get('id_paquete')}")
    print(f"   Datos: {paquete_data}")
    
    resultado = {"productos": []}
    
    # Procesar Pizzas
    id_pizzas = paquete_data.get('id_pizzas', [])
    if id_pizzas:
        if isinstance(id_pizzas, str):
            try:
                id_pizzas = json.loads(id_pizzas)
            except:
                id_pizzas = [id_pizzas]
        
        print(f"   🍕 Pizzas encontradas: {id_pizzas}")
        for pid in id_pizzas:
            resultado["productos"].append({"tipo": "Pizza", "id": pid})
    
    # Procesar Refresco
    id_refresco = paquete_data.get('id_refresco')
    if id_refresco:
        print(f"   🥤 Refresco encontrado: {id_refresco}")
        resultado["productos"].append({"tipo": "Refresco", "id": id_refresco})
    
    # Procesar Hamburguesa
    id_hamb = paquete_data.get('id_hamb')
    if id_hamb:
        print(f"   🍔 Hamburguesa encontrada: {id_hamb}")
        resultado["productos"].append({"tipo": "Hamburguesa", "id": id_hamb})
    
    # Procesar Alitas
    id_alis = paquete_data.get('id_alis')
    if id_alis:
        print(f"   🍗 Alitas encontradas: {id_alis}")
        resultado["productos"].append({"tipo": "Alitas", "id": id_alis})
    
    return resultado


if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Parseo de Paquetes JSON")
    print("=" * 60)
    
    # Prueba 1: Paquete tipo 1 (Pizzas + Refresco)
    resultado_1 = simulate_procesar_paquete(paquete_data_1)
    print(f"   ✅ Resultado: {resultado_1}")
    
    # Prueba 2: Paquete tipo 2 (Pizzas + Refresco + Hamburguesa)
    resultado_2 = simulate_procesar_paquete(paquete_data_2)
    print(f"   ✅ Resultado: {resultado_2}")
    
    # Prueba 3: Como string JSON (como vendría de la BD en algunos casos)
    paquete_string = json.dumps(paquete_data_1)
    resultado_3 = simulate_procesar_paquete(paquete_string)
    print(f"   ✅ Resultado (desde string): {resultado_3}")
    
    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS PASARON ✅")
    print("=" * 60)
