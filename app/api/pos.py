from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, update
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional

from app.db.session import get_session
from app.models.detallesModel import DetalleVenta
from app.models.ventaModel import Venta
from app.models.pagosModel import Pago
from app.models.pDireccionModel import pDireccion
from app.models.DireccionesModel import Direccion

from app.schemas.ventaSchema import VentaRequest, VentaResponse, RegistrarPagoRequest

from app.models.clienteModel import Cliente
from app.models.sucursalModel import Sucursal

router = APIRouter()


@router.get("/pedidos-resumen")
async def listar_pedidos_resumen(
    session: Session = Depends(get_session),
    filtro: str = "hoy",
    status: Optional[int] = None,
    id_suc: Optional[int] = None,
):
    try:
        statement = select(Venta).order_by(Venta.fecha_hora.desc())

        now = datetime.now()
        
        if filtro == "hoy":
            hoy_inicio = now.replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = hoy_inicio + timedelta(days=1)
            statement = statement.where(
                Venta.fecha_hora >= hoy_inicio,
                Venta.fecha_hora < hoy_fin
            )
        elif filtro == "semana":
            inicio_semana = now - timedelta(days=now.weekday())
            inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
            statement = statement.where(Venta.fecha_hora >= inicio_semana)
        elif filtro == "mes":
            inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            statement = statement.where(Venta.fecha_hora >= inicio_mes)
        elif filtro == "todos":
            pass

        if status is not None:
            statement = statement.where(Venta.status == status)

        if id_suc:
            statement = statement.where(Venta.id_suc == id_suc)

        ventas = session.exec(statement).all()

        pedidos_resumen = []
        for venta in ventas:
            # Obtener cliente según el tipo de servicio
            nombre_cliente = None
            
            if venta.tipo_servicio == 0:  # Comer aquí
                # Mostrar Mesa X - Nombre del cliente
                mesa_num = venta.mesa if venta.mesa else "S/N"
                nombre_base = venta.nombreClie if venta.nombreClie else "Sin nombre"
                nombre_cliente = f"Mesa {mesa_num} - {nombre_base}"
                    
            elif venta.tipo_servicio == 1:  # Para llevar
                # Solo mostrar el nombre del cliente
                nombre_cliente = venta.nombreClie if venta.nombreClie else "Para llevar"
                    
            elif venta.tipo_servicio == 2:  # Domicilio
                # Se queda como está (buscar en pDireccion)
                statement_domicilio = select(pDireccion).where(pDireccion.id_venta == venta.id_venta)
                domicilio = session.exec(statement_domicilio).first()
                
                if domicilio and domicilio.id_clie:
                    cliente = session.get(Cliente, domicilio.id_clie)
                    nombre_cliente = cliente.nombre if cliente else "Cliente sin nombre"
                else:
                    nombre_cliente = venta.nombreClie if venta.nombreClie else "Domicilio sin cliente"

            # Valor por defecto si algo falló
            if not nombre_cliente:
                nombre_cliente = "Sin información"

            sucursal = session.get(Sucursal, venta.id_suc)
            nombre_sucursal = sucursal.nombre if sucursal else "Desconocida"

            statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == venta.id_venta)
            detalles = session.exec(statement_detalles).all()
            total_items = sum(det.cantidad for det in detalles)

            pedidos_resumen.append({
                "id_venta": venta.id_venta,
                "fecha_hora": venta.fecha_hora,
                "cliente": nombre_cliente,
                "tipo_servicio": venta.tipo_servicio,
                "tipo_servicio_texto": {
                    0: "Comer aquí",
                    1: "Para llevar",
                    2: "Domicilio"
                }.get(venta.tipo_servicio, "Desconocido"),
                "mesa": venta.mesa if venta.tipo_servicio == 0 else None,
                "sucursal": nombre_sucursal,
                "status": venta.status,
                "status_texto": {
                    0: "Esperando",
                    1: "Preparando",
                    2: "Completado"
                }.get(venta.status, "Desconocido"),
                "total": float(venta.total),
                "cantidad_items": total_items
            })

        return {
            "pedidos": pedidos_resumen,
            "total": len(pedidos_resumen),
            "filtro_aplicado": filtro,
            "status_filtrado": status,
            "sucursal_filtrada": id_suc
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")



@router.get("/pedidos-cocina")
async def listar_pedidos_cocina(
    session: Session = Depends(get_session),
    filtro: str = "hoy",
    id_suc: Optional[int] = None,
):
    try:
        # Construir query base
        statement = select(Venta).order_by(Venta.fecha_hora.asc())

        # Filtro por fecha
        if filtro == "hoy":
            hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = hoy_inicio + timedelta(days=1)
            statement = statement.where(
                Venta.fecha_hora >= hoy_inicio,
                Venta.fecha_hora < hoy_fin
            )

        # Filtrar por status: solo mostrar Esperando (0) y Preparando (1)
        statement = statement.where(Venta.status.in_([0, 1]))

        # Filtro por sucursal
        if id_suc:
            statement = statement.where(Venta.id_suc == id_suc)

        ventas = session.exec(statement).all()

        pedidos_cocina = []
        for venta in ventas:
            # Obtener cliente según el tipo de servicio
            nombre_cliente = None
            
            if venta.tipo_servicio == 0:
                mesa_num = venta.mesa if venta.mesa else "S/N"
                nombre_base = venta.nombreClie if venta.nombreClie else "Sin nombre"
                nombre_cliente = f"Mesa {mesa_num} - {nombre_base}"
                    
            elif venta.tipo_servicio == 1:
                nombre_cliente = venta.nombreClie if venta.nombreClie else "Para llevar"
                    
            elif venta.tipo_servicio == 2:
                statement_domicilio = select(pDireccion).where(pDireccion.id_venta == venta.id_venta)
                domicilio = session.exec(statement_domicilio).first()
                
                if domicilio and domicilio.id_clie:
                    cliente = session.get(Cliente, domicilio.id_clie)
                    nombre_cliente = cliente.nombre if cliente else "Cliente sin nombre"
                else:
                    nombre_cliente = venta.nombreClie if venta.nombreClie else "Domicilio sin cliente"

            # Valor por defecto si algo falló
            if not nombre_cliente:
                nombre_cliente = "Sin información"

            # Obtener sucursal
            sucursal = session.get(Sucursal, venta.id_suc)
            nombre_sucursal = sucursal.nombre if sucursal else "Desconocida"

            # Obtener detalles de productos
            statement_detalles = select(DetalleVenta).where(
                DetalleVenta.id_venta == venta.id_venta,
                DetalleVenta.status.in_([0, 1, 2])
            )
            detalles = session.exec(statement_detalles).all()

            # Construir lista de productos con nombres
            productos = []
            for det in detalles:
                producto_info = {
                    "cantidad": det.cantidad,
                    "nombre": None,
                    "tipo": None,
                    "status": det.status
                }

                if det.id_pizza and det.id_paquete != 2:
                    from app.models.pizzasModel import pizzas
                    producto = session.get(pizzas, det.id_pizza)
                    if producto:
                        try:
                            from app.models.especialidadModel import especialidad
                            especialidad_obj = session.get(especialidad, producto.id_esp)
                            nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                        except:
                            nombre_especialidad = f"Especialidad #{producto.id_esp}"

                        producto_info["nombre"] = nombre_especialidad
                        producto_info["tipo"] = "Pizza"
                    productos.append(producto_info)
                    
                if det.id_hamb and det.id_paquete != 2:
                    from app.models.hamburguesasModel import hamburguesas
                    producto = session.get(hamburguesas, det.id_hamb)
                    if producto:
                        producto_info["nombre"] = producto.paquete
                        producto_info["tipo"] = "Hamburguesa"
                    productos.append(producto_info)
                
                if det.id_cos:
                    from app.models.costillasModel import costillas
                    producto = session.get(costillas, det.id_cos)
                    if producto:
                        producto_info["nombre"] = producto.orden
                        producto_info["tipo"] = "Costilla"
                    productos.append(producto_info)
                
                if det.id_alis and det.id_paquete != 2:
                    from app.models.alitasModel import alitas
                    producto = session.get(alitas, det.id_alis)
                    if producto:
                        producto_info["nombre"] = producto.orden
                        producto_info["tipo"] = "Alitas"
                    productos.append(producto_info)
                
                if det.id_spag:
                    from app.models.spaguettyModel import spaguetty
                    producto = session.get(spaguetty, det.id_spag)
                    if producto:
                        producto_info["nombre"] = producto.orden
                        producto_info["tipo"] = "Spaghetti"
                    productos.append(producto_info)
                
                if det.id_papa:
                    from app.models.papasModel import papas
                    producto = session.get(papas, det.id_papa)
                    if producto:
                        producto_info["nombre"] = producto.orden
                        producto_info["tipo"] = "Papas"
                    productos.append(producto_info)
                
                if det.id_maris:
                    from app.models.mariscosModel import mariscos
                    producto = session.get(mariscos, det.id_maris)
                    if producto:
                        producto_info["nombre"] = producto.nombre
                        producto_info["tipo"] = "Mariscos"
                    productos.append(producto_info)
                
                if det.id_refresco and det.id_paquete != 2:
                    from app.models.refrescosModel import refrescos
                    producto = session.get(refrescos, det.id_refresco)
                    if producto:
                        producto_info["nombre"] = producto.nombre
                        producto_info["tipo"] = "Refresco"
                    productos.append(producto_info)
                
                if det.id_magno:
                    from app.models.magnoModel import magno
                    producto = session.get(magno, det.id_magno)
                    if producto:
                        try:
                            from app.models.especialidadModel import especialidad
                            especialidad_obj = session.get(especialidad, producto.id_especialidad)
                            nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                        except:
                            nombre_especialidad = f"Especialidad #{producto.id_especialidad}"

                        producto_info["nombre"] = nombre_especialidad
                        producto_info["tipo"] = "Magno"
                    productos.append(producto_info)
                
                if det.id_rec:
                    from app.models.rectangularModel import rectangular
                    producto = session.get(rectangular, det.id_rec)
                    if producto:
                        try:
                            from app.models.especialidadModel import especialidad
                            especialidad_obj = session.get(especialidad, producto.id_esp)
                            nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                        except:
                            nombre_especialidad = f"Especialidad #{producto.id_esp}"

                        producto_info["nombre"] = nombre_especialidad
                        producto_info["tipo"] = "Rectangular"
                    productos.append(producto_info)
                
                if det.id_paquete:
                    if det.id_paquete in [1, 3]:
                        from app.models.pizzasModel import pizzas
                        from app.models.especialidadModel import especialidad
                        
                        if det.detalle_paquete:
                            ids_pizzas = det.detalle_paquete.split(",")
                            
                            for id_pizza_str in ids_pizzas:
                                try:
                                    id_pizza = int(id_pizza_str.strip())
                                    pizza = session.get(pizzas, id_pizza)
                                    
                                    if pizza:
                                        try:
                                            especialidad_obj = session.get(especialidad, pizza.id_esp)
                                            nombre_especialidad = especialidad_obj.nombre if especialidad_obj else f"Especialidad #{pizza.id_esp}"
                                        except:
                                            nombre_especialidad = f"Especialidad #{pizza.id_esp}"
                                        
                                        pizza_info = {
                                            "cantidad": 1,
                                            "nombre": nombre_especialidad,
                                            "tipo": f"Paquete {det.id_paquete} - Pizza",
                                            "status": det.status
                                        }
                                        productos.append(pizza_info)
                                
                                except (ValueError, AttributeError) as e:
                                    error_info = {
                                        "cantidad": 1,
                                        "nombre": f"Error al cargar pizza del paquete",
                                        "tipo": f"Paquete {det.id_paquete}",
                                        "status": det.status
                                    }
                                    productos.append(error_info)
                        else:
                            producto_info["nombre"] = f"Paquete {det.id_paquete} - Sin detalle"
                            producto_info["tipo"] = "Paquete"
                            producto_info["status"] = det.status
                            productos.append(producto_info)
                    elif det.id_paquete == 2:
                        from app.models.pizzasModel import pizzas
                        from app.models.especialidadModel import especialidad
                        from app.models.alitasModel import alitas
                        from app.models.refrescosModel import refrescos
                        from app.models.hamburguesasModel import hamburguesas
                        
                        refresco = session.get(refrescos, det.id_refresco)
                        if refresco:
                            refresco_info = {
                                "cantidad": 1,
                                "nombre": refresco.nombre,
                                "tipo": f"Paquete {det.id_paquete} - Refresco",
                                "status": det.status
                            }
                            productos.append(refresco_info)
                        
                        producto = session.get(pizzas, det.id_pizza)
                        if producto:
                            try:
                                especialidad_obj = session.get(especialidad, producto.id_esp)
                                nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                            except:
                                nombre_especialidad = f"Especialidad #{producto.id_esp}"
                            pizza_info = {
                                "cantidad": 1,
                                "nombre": nombre_especialidad,
                                "tipo": f"Paquete {det.id_paquete} - Pizza",
                                "status": det.status
                            }
                            productos.append(pizza_info)
                        if det.id_alis:
                            alita = session.get(alitas, det.id_alis)
                            if alita:
                                alita_info = {
                                    "cantidad": 1,
                                    "nombre": alita.orden,
                                    "tipo": f"Paquete {det.id_paquete} - Alitas",
                                    "status": det.status
                                }
                                productos.append(alita_info)
                        else:
                            hamburguesa = session.get(hamburguesas, det.id_hamb)
                            if hamburguesa:
                                hamb_info = {
                                    "cantidad": 1,
                                    "nombre": hamburguesa.paquete,
                                    "tipo": f"Paquete {det.id_paquete} - Hamburguesa",
                                    "status": det.status
                                }
                                productos.append(hamb_info)
                        
            total_items = sum(det.cantidad for det in detalles)
            
            # Calcular tiempo transcurrido
            tiempo_transcurrido = datetime.now() - venta.fecha_hora
            minutos_transcurridos = int(tiempo_transcurrido.total_seconds() / 60)

            pedidos_cocina.append({
                "id_venta": venta.id_venta,
                "fecha_hora": venta.fecha_hora,
                "tiempo_transcurrido_minutos": minutos_transcurridos,
                "cliente": nombre_cliente,
                "tipo_servicio": venta.tipo_servicio,
                "tipo_servicio_texto": {
                    0: "Comer aquí",
                    1: "Para llevar",
                    2: "Domicilio"
                }.get(venta.tipo_servicio, "Desconocido"),
                "mesa": venta.mesa if venta.tipo_servicio == 0 else None,
                "sucursal": nombre_sucursal,
                "status": venta.status,
                "comentarios": venta.comentarios,
                "status_texto": {
                    0: "Esperando",
                    1: "Preparando",
                    2: "Completado"
                }.get(venta.status, "Desconocido"),
                "cantidad_items": total_items,
                "cantidad_productos_diferentes": len(detalles),
                "productos": productos
            })

        return {
            "pedidos": pedidos_cocina,
            "total": len(pedidos_cocina),
            "filtro_aplicado": filtro,
            "status_filtrado": None,
            "sucursal_filtrada": id_suc
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pedidos: {str(e)}")



@router.get("/edit/{id_venta}/detalle")
async def getDetallesEdit(
    id_venta: int,
    session: Session = Depends(get_session)
):
    try:
        # Obtener venta
        venta = session.get(Venta, id_venta)
        if not venta:
            raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")

        # Obtener sucursal
        sucursal = session.get(Sucursal, venta.id_suc)
        nombre_sucursal = sucursal.nombre if sucursal else "Desconocida"

        # Obtener detalles de productos
        statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles = session.exec(statement_detalles).all()

        # Construir lista de productos con nombres
        productos = []
        for det in detalles:
            producto_info = {
                "cantidad": det.cantidad,
                "id": None,
                "tipo": None,
                "tamaño": None,
                "status": det.status
            }

            if det.id_pizza and not det.id_paquete:
                from app.models.pizzasModel import pizzas
                from app.models.tamanosPizzasModel import tamanosPizzas
                
                producto = session.get(pizzas, det.id_pizza)
                if producto:
                    tamano_obj = session.get(tamanosPizzas, producto.id_tamano)
                    nombre_tamano = tamano_obj.tamano if tamano_obj else "Tamaño desconocido"

                    producto_info["id"] = producto.id_pizza
                    producto_info["tamaño"] = nombre_tamano
                    producto_info["tipo"] = "id_pizza"
                productos.append(producto_info)
                
            elif det.id_hamb and not det.id_paquete:
                producto_info["id"] = det.id_hamb
                producto_info["tipo"] = "id_hamb"
                productos.append(producto_info)
            
            elif det.id_cos and not det.id_paquete:
                producto_info["id"] = det.id_cos
                producto_info["tipo"] = "id_cos"
                productos.append(producto_info)
            
            elif det.id_alis and not det.id_paquete:
                producto_info["id"] = det.id_alis
                producto_info["tipo"] = "id_alis"
                productos.append(producto_info)
            
            elif det.id_spag and not det.id_paquete:
                producto_info["id"] = det.id_spag
                producto_info["tipo"] = "id_spag"
                productos.append(producto_info)
            
            elif det.id_papa and not det.id_paquete:
                producto_info["id"] = det.id_papa
                producto_info["tipo"] = "id_papa"
                productos.append(producto_info)
            
            elif det.id_maris and not det.id_paquete:
                producto_info["id"] = det.id_maris
                producto_info["tipo"] = "id_maris"
                productos.append(producto_info)
            
            elif det.id_refresco and not det.id_paquete:
                from app.models.refrescosModel import refrescos
                from app.models.tamanosRefrescosModel import tamanosRefrescos
                producto = session.get(refrescos, det.id_refresco)
                tamano = session.get(tamanosRefrescos, producto.id_tamano)
                if producto:
                    producto_info["id"] = producto.id_refresco
                    producto_info["tipo"] = "id_refresco"
                    producto_info["tamaño"] = tamano.tamano
                productos.append(producto_info)
            
            elif det.id_magno and not det.id_paquete:
                producto_info["id"] = det.id_magno
                producto_info["tipo"] = "id_magno"
                productos.append(producto_info)
            
            elif det.id_rec and not det.id_paquete:
                producto_info["id"] = det.id_rec
                producto_info["tipo"] = "id_rec"
                productos.append(producto_info)
            
            elif det.id_paquete:
                producto_info["id"] = det.id_paquete
                producto_info["tipo"] = "id_paquete"
                productos.append(producto_info)

        # Construir respuesta base
        response = {
            "id_venta": venta.id_venta,
            "fecha_hora": venta.fecha_hora,
            "id_suc": venta.id_suc,
            "sucursal": nombre_sucursal,
            "tipo_servicio": venta.tipo_servicio,
            "status": venta.status,
            "comentarios": venta.comentarios,
            "status_texto": {
                0: "Esperando",
                1: "Preparando",
                2: "Completado"
            }.get(venta.status, "Desconocido"),
            "productos": productos
        }

        # Añadir campos según tipo_servicio
        if venta.tipo_servicio == 0:  # Comedor
            response["mesa"] = venta.mesa
            response["nombreClie"] = venta.nombreClie
        
        elif venta.tipo_servicio == 1:  # Para Llevar
            response["nombreClie"] = venta.nombreClie
            
            # Obtener pagos
            from app.models.pagosModel import Pago
            statement_pagos = select(Pago).where(Pago.id_venta == id_venta)
            pagos = session.exec(statement_pagos).all()
            
            response["pagos"] = [
                {
                    "id_metpago": pago.id_metpago,
                    "monto": pago.monto
                }
                for pago in pagos
            ]
        
        elif venta.tipo_servicio == 2:
            response["id_cliente"] = getattr(venta, 'id_cliente', None)
            response["id_direccion"] = getattr(venta, 'id_direccion', None)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalle del pedido: {str(e)}")



@router.get("/pedidos-cocina/{id_venta}/detalle")
async def obtener_detalle_pedido_cocina(
    id_venta: int,
    session: Session = Depends(get_session)
):
    try:
        # Obtener venta
        venta = session.get(Venta, id_venta)
        if not venta:
            raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")

        # Obtener cliente según el tipo de servicio (misma lógica que en el listado)
        nombre_cliente = None
        if venta.tipo_servicio == 2:  # Domicilio
            # Buscar en pDireccion
            statement_domicilio = select(pDireccion).where(pDireccion.id_venta == venta.id_venta)
            domicilio = session.exec(statement_domicilio).first()
            
            if domicilio:
                cliente = session.get(Cliente, domicilio.id_clie)
                nombre_cliente = cliente.nombre if cliente else "Desconocido"
        
        # Si no es domicilio o no se encontró cliente, usar valores por defecto según tipo
        if not nombre_cliente:
            if venta.tipo_servicio == 0:
                nombre_cliente = f"Mesa {venta.mesa}" if venta.mesa else "Mesa sin número"
            elif venta.tipo_servicio == 1:
                nombre_cliente = "Para llevar"
            else:
                nombre_cliente = "Sin información"

        # Obtener sucursal
        sucursal = session.get(Sucursal, venta.id_suc)
        nombre_sucursal = sucursal.nombre if sucursal else "Desconocida"

        # Obtener detalles de productos
        statement_detalles = select(DetalleVenta).where(
            DetalleVenta.id_venta == id_venta,
            DetalleVenta.status.in_([0, 1, 2])  # Solo los status válidos
        )
        detalles = session.exec(statement_detalles).all()

        # Construir lista de productos con nombres
        productos = []
        for det in detalles:
            producto_info = {
                "cantidad": det.cantidad,
                "nombre": None,
                "tipo": None,
                "status": det.status  # <-- Añadido status del detalle
            }

            if det.id_pizza and det.id_paquete != 2:
                from app.models.pizzasModel import pizzas
                producto = session.get(pizzas, det.id_pizza)
                if producto:
                    try:
                        from app.models.especialidadModel import especialidad
                        especialidad_obj = session.get(especialidad, producto.id_esp)
                        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                    except:
                        nombre_especialidad = f"Especialidad #{producto.id_esp}"

                    producto_info["nombre"] = nombre_especialidad
                    producto_info["tipo"] = "Pizza"
                productos.append(producto_info)
                
            if det.id_hamb and det.id_paquete != 2:
                from app.models.hamburguesasModel import hamburguesas
                producto = session.get(hamburguesas, det.id_hamb)
                if producto:
                    producto_info["nombre"] = producto.paquete
                    producto_info["tipo"] = "Hamburguesa"
                productos.append(producto_info)
            
            if det.id_cos:
                from app.models.costillasModel import costillas
                producto = session.get(costillas, det.id_cos)
                if producto:
                    producto_info["nombre"] = producto.orden
                    producto_info["tipo"] = "Costilla"
                productos.append(producto_info)
            
            if det.id_alis and det.id_paquete != 2:
                from app.models.alitasModel import alitas
                producto = session.get(alitas, det.id_alis)
                if producto:
                    producto_info["nombre"] = producto.orden
                    producto_info["tipo"] = "Alitas"
                productos.append(producto_info)
            
            if det.id_spag:
                from app.models.spaguettyModel import spaguetty
                producto = session.get(spaguetty, det.id_spag)
                if producto:
                    producto_info["nombre"] = producto.orden
                    producto_info["tipo"] = "Spaghetti"
                productos.append(producto_info)
            
            if det.id_papa:
                from app.models.papasModel import papas
                producto = session.get(papas, det.id_papa)
                if producto:
                    producto_info["nombre"] = producto.orden
                    producto_info["tipo"] = "Papas"
                productos.append(producto_info)
            
            if det.id_maris:
                from app.models.mariscosModel import mariscos
                producto = session.get(mariscos, det.id_maris)
                if producto:
                    producto_info["nombre"] = producto.nombre
                    producto_info["tipo"] = "Mariscos"
                productos.append(producto_info)
            
            if det.id_refresco and det.id_paquete != 2:
                from app.models.refrescosModel import refrescos
                producto = session.get(refrescos, det.id_refresco)
                if producto:
                    producto_info["nombre"] = producto.nombre
                    producto_info["tipo"] = "Refresco"
                productos.append(producto_info)
            
            if det.id_magno:
                from app.models.magnoModel import magno
                producto = session.get(magno, det.id_magno)
                if producto:
                    try:
                        from app.models.especialidadModel import especialidad
                        especialidad_obj = session.get(especialidad, producto.id_especialidad)
                        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                    except:
                        nombre_especialidad = f"Especialidad #{producto.id_especialidad}"

                    producto_info["nombre"] = nombre_especialidad
                    producto_info["tipo"] = "Magno"
                productos.append(producto_info)
            
            if det.id_rec:
                from app.models.rectangularModel import rectangular
                producto = session.get(rectangular, det.id_rec)
                if producto:
                    try:
                        from app.models.especialidadModel import especialidad
                        especialidad_obj = session.get(especialidad, producto.id_esp)
                        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                    except:
                        nombre_especialidad = f"Especialidad #{producto.id_esp}"

                    producto_info["nombre"] = nombre_especialidad
                    producto_info["tipo"] = "Rectangular"
                productos.append(producto_info)
            
            if det.id_paquete:
                if det.id_paquete in [1, 3]:
                    from app.models.pizzasModel import pizzas
                    from app.models.especialidadModel import especialidad
                    
                    # Parse los IDs del string (ej: "1,2" o "1,2,3")
                    if det.detalle_paquete:
                        ids_pizzas = det.detalle_paquete.split(",")
                        
                        for id_pizza_str in ids_pizzas:
                            try:
                                id_pizza = int(id_pizza_str.strip())
                                pizza = session.get(pizzas, id_pizza)
                                
                                if pizza:
                                    try:
                                        especialidad_obj = session.get(especialidad, pizza.id_esp)
                                        nombre_especialidad = especialidad_obj.nombre if especialidad_obj else f"Especialidad #{pizza.id_esp}"
                                    except:
                                        nombre_especialidad = f"Especialidad #{pizza.id_esp}"
                                    
                                    pizza_info = {
                                        "cantidad": 1,
                                        "nombre": nombre_especialidad,
                                        "tipo": f"Paquete {det.id_paquete} - Pizza",
                                        "status": det.status  # <-- Añadido status del detalle
                                    }
                                    productos.append(pizza_info)
                            
                            except (ValueError, AttributeError) as e:
                                error_info = {
                                    "cantidad": 1,
                                    "nombre": f"Error al cargar pizza del paquete",
                                    "tipo": f"Paquete {det.id_paquete}",
                                    "status": det.status  # <-- Añadido status del detalle
                                }
                                productos.append(error_info)
                    else:
                        producto_info["nombre"] = f"Paquete {det.id_paquete} - Sin detalle"
                        producto_info["tipo"] = "Paquete"
                        producto_info["status"] = det.status  # <-- Añadido status del detalle
                        productos.append(producto_info)
                elif det.id_paquete == 2:
                    from app.models.pizzasModel import pizzas
                    from app.models.especialidadModel import especialidad
                    from app.models.alitasModel import alitas
                    from app.models.refrescosModel import refrescos
                    from app.models.hamburguesasModel import hamburguesas
                    
                    refresco = session.get(refrescos, det.id_refresco)
                    if refresco:
                        refresco_info = {
                            "cantidad": 1,
                            "nombre": refresco.nombre,
                            "tipo": f"Paquete {det.id_paquete} - Refresco",
                            "status": det.status  # <-- Añadido status del detalle
                        }
                        productos.append(refresco_info)
                    
                    producto = session.get(pizzas, det.id_pizza)
                    if producto:
                        try:
                            especialidad_obj = session.get(especialidad, producto.id_esp)
                            nombre_especialidad = especialidad_obj.nombre if especialidad_obj else "Especialidad desconocida"
                        except:
                            nombre_especialidad = f"Especialidad #{producto.id_esp}"
                        pizza_info = {
                            "cantidad": 1,
                            "nombre": nombre_especialidad,
                            "tipo": f"Paquete {det.id_paquete} - Pizza",
                            "status": det.status  # <-- Añadido status del detalle
                        }
                        productos.append(pizza_info)
                    if det.id_alis:
                        alita = session.get(alitas, det.id_alis)
                        if alita:
                            alita_info = {
                                "cantidad": 1,
                                "nombre": alita.orden,
                                "tipo": f"Paquete {det.id_paquete} - Alitas",
                                "status": det.status  # <-- Añadido status del detalle
                            }
                            productos.append(alita_info)
                    else:
                        hamburguesa = session.get(hamburguesas, det.id_hamb)
                        if hamburguesa:
                            hamb_info = {
                                "cantidad": 1,
                                "nombre": hamburguesa.paquete,
                                "tipo": f"Paquete {det.id_paquete} - Hamburguesa",
                                "status": det.status  # <-- Añadido status del detalle
                            }
                            productos.append(hamb_info)
                        
                        

        total_items = sum(det.cantidad for det in detalles)
        tiempo_transcurrido = datetime.now() - venta.fecha_hora
        minutos_transcurridos = int(tiempo_transcurrido.total_seconds() / 60)

        return {
            "id_venta": venta.id_venta,
            "fecha_hora": venta.fecha_hora,
            "tiempo_transcurrido_minutos": minutos_transcurridos,
            "cliente": nombre_cliente,
            "tipo_servicio": venta.tipo_servicio,
            "tipo_servicio_texto": {
                0: "Comer aquí",
                1: "Para llevar",
                2: "Domicilio"
            }.get(venta.tipo_servicio, "Desconocido"),
            "mesa": venta.mesa if venta.tipo_servicio == 0 else None,
            "sucursal": nombre_sucursal,
            "status": venta.status,
            "comentarios": venta.comentarios,
            "status_texto": {
                0: "Esperando",
                1: "Preparando",
                2: "Completado"
            }.get(venta.status, "Desconocido"),
            "cantidad_items": total_items,
            "cantidad_productos_diferentes": len(detalles),
            "productos": productos
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener detalle del pedido: {str(e)}")


@router.post("/")
async def crear_venta(
    venta_request: VentaRequest,
    session: Session = Depends(get_session)
):
    if not venta_request.items:
        raise HTTPException(status_code=400, detail="La venta debe contener al menos un item")

    # Validar pagos si tipo_servicio es 1
    if venta_request.tipo_servicio == 1:
        if not venta_request.pagos or len(venta_request.pagos) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar al menos un método de pago cuando el tipo de servicio es 1 (para llevar)"
            )

    # Validar cliente solo si tipo_servicio es 2 (domicilio)
    if venta_request.tipo_servicio == 2:
        if not venta_request.id_cliente:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el id_cliente cuando el tipo de servicio es 2 (domicilio)"
            )
        
        cliente = session.get(Cliente, venta_request.id_cliente)
        if not cliente:
            raise HTTPException(
                status_code=404, 
                detail=f"Cliente con ID {venta_request.id_cliente} no encontrado"
            )
        
        # Validar que la dirección existe
        if not venta_request.id_direccion:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el id_direccion cuando el tipo de servicio es 2 (domicilio)"
            )
        
        direccion = session.get(Direccion, venta_request.id_direccion)
        if not direccion:
            raise HTTPException(
                status_code=404, 
                detail=f"Dirección con ID {venta_request.id_direccion} no encontrada"
            )

    # Validar mesa si tipo_servicio es 0 (comer aquí)
    if venta_request.tipo_servicio == 0:
        if venta_request.mesa is None:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el número de mesa cuando el tipo de servicio es 0 (comer aquí)"
            )

    # Validar sucursal
    sucursal = session.get(Sucursal, venta_request.id_suc)
    if not sucursal:
        raise HTTPException(
            status_code=404, 
            detail=f"Sucursal con ID {venta_request.id_suc} no encontrada"
        )

    try:
        # Crear la venta
        nueva_venta = Venta(
            id_suc=venta_request.id_suc,
            mesa=venta_request.mesa if venta_request.tipo_servicio == 0 else None,
            fecha_hora=datetime.now(),
            total=Decimal(str(venta_request.total)),
            comentarios=venta_request.comentarios,
            tipo_servicio=venta_request.tipo_servicio,
            status=venta_request.status,
            nombreClie=venta_request.nombreClie
        )
        session.add(nueva_venta)
        session.flush()
        
        # Si es domicilio (tipo_servicio = 2), crear registro en pDireccion
        if venta_request.tipo_servicio == 2:
            nuevo_domicilio = pDireccion(
                id_clie=venta_request.id_cliente,
                id_dir=venta_request.id_direccion,
                id_venta=nueva_venta.id_venta
            )
            session.add(nuevo_domicilio)
        
        # Crear pagos si tipo_servicio es 1 (para llevar)
        pagos_creados = []
        if venta_request.tipo_servicio == 1 and venta_request.pagos:
            for pago_request in venta_request.pagos:
                nuevo_pago = Pago(
                    id_venta=nueva_venta.id_venta,
                    id_metpago=pago_request.id_metpago,
                    monto=Decimal(str(pago_request.monto))
                )
                session.add(nuevo_pago)
                pagos_creados.append({
                    "id_metpago": pago_request.id_metpago,
                    "monto": float(pago_request.monto)
                })

        # Crear los detalles de la venta
        for item in venta_request.items:
            nuevo_detalle = DetalleVenta(
                id_venta=nueva_venta.id_venta,
                cantidad=item.cantidad,
                precio_unitario=Decimal(str(item.precio_unitario)),
                id_hamb=item.id_hamb,
                id_cos=item.id_cos,
                id_alis=item.id_alis,
                id_spag=item.id_spag,
                id_papa=item.id_papa,
                id_rec=item.id_rec,
                id_barr=item.id_barr,
                id_maris=item.id_maris,
                id_refresco=item.id_refresco,
                id_paquete=item.id_paquete,
                detalle_paquete=item.detalle_paquete,
                id_magno=item.id_magno,
                id_pizza=item.id_pizza
            )
            session.add(nuevo_detalle)

        session.commit()
        
        # Obtener los detalles para la respuesta
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == nueva_venta.id_venta)
        detalles_db = session.exec(statement).all()
        
        detalles_respuesta = []
        for det in detalles_db:
            subtotal = det.cantidad * det.precio_unitario
            detalles_respuesta.append({
                "cantidad": det.cantidad,
                "precio_unitario": float(det.precio_unitario),
                "subtotal": float(subtotal)
            })

        respuesta = {
            "Mensaje": "Venta creada exitosamente",
            "id_venta": nueva_venta.id_venta,
            "total": float(nueva_venta.total),
            "tipo_servicio": nueva_venta.tipo_servicio
        }
        
        # Agregar información específica según el tipo de servicio
        if venta_request.tipo_servicio == 0:
            respuesta["mesa"] = nueva_venta.mesa
        elif venta_request.tipo_servicio == 1:
            respuesta["pagos_registrados"] = pagos_creados
            respuesta["numero_pagos"] = len(pagos_creados)
        elif venta_request.tipo_servicio == 2:
            respuesta["id_cliente"] = venta_request.id_cliente
            respuesta["id_direccion"] = venta_request.id_direccion
        
        # Agregar nombreClie a la respuesta si existe
        if venta_request.nombreClie:
            respuesta["nombreClie"] = venta_request.nombreClie
        
        return respuesta

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la venta: {str(e)}")



@router.post("/pagar")
async def registrar_pago_venta(
    pago_request: RegistrarPagoRequest,
    session: Session = Depends(get_session)
):
    # Verificar que la venta existe
    venta = session.get(Venta, pago_request.id_venta)
    if not venta:
        raise HTTPException(
            status_code=404, 
            detail=f"Venta con ID {pago_request.id_venta} no encontrada"
        )
    
    # Verificar que la venta sea tipo 0 (Para llevar) o 2 (Domicilio)
    if venta.tipo_servicio not in [0, 2]:
        raise HTTPException(
            status_code=400,
            detail=f"Este endpoint es solo para ventas tipo 0 (Para llevar) o 2 (Domicilio). Esta venta es tipo {venta.tipo_servicio}"
        )
    
    # Verificar si ya tiene pagos registrados
    statement = select(Pago).where(Pago.id_venta == pago_request.id_venta)
    pagos_existentes = session.exec(statement).all()
    
    if pagos_existentes:
        raise HTTPException(
            status_code=400,
            detail=f"Esta venta ya tiene pagos registrados. Use el endpoint de actualizar pagos si desea modificarlos."
        )
    
    try:
        # Calcular la suma de los pagos
        suma_pagos = sum(pago.monto for pago in pago_request.pagos)
        
        # Validar que la suma de los pagos coincida con el total de la venta
        if abs(suma_pagos - venta.total) > Decimal('0.01'):  # Tolerancia de 1 centavo
            raise HTTPException(
                status_code=400,
                detail=f'La suma de los pagos ({suma_pagos}) debe ser igual al total de la venta ({venta.total})'
            )
        
        # Crear los registros de pago
        pagos_creados = []
        for pago_data in pago_request.pagos:
            nuevo_pago = Pago(
                id_venta=pago_request.id_venta,
                id_metpago=pago_data.id_metpago,
                monto=Decimal(str(pago_data.monto))
            )
            session.add(nuevo_pago)
            pagos_creados.append({
                "id_metpago": pago_data.id_metpago,
                "monto": float(pago_data.monto)
            })
        
        # Actualizar el status de la venta si es necesario
        # Por ejemplo, podrías cambiar status=0 (pendiente) a status=1 (pagada)
        venta.status = 1
        
        session.commit()
        
        return {
            "Mensaje": "Pago registrado exitosamente",
            "id_venta": pago_request.id_venta,
            "total_venta": float(venta.total),
            "total_pagado": float(suma_pagos),
            "pagos_registrados": pagos_creados,
            "numero_pagos": len(pagos_creados),
            "status_actualizado": venta.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al registrar el pago: {str(e)}"
        )



@router.get("/{id_venta}", response_model=VentaResponse)
async def obtener_venta(
    id_venta: int,
    session: Session = Depends(get_session)
):
    # Obtener venta
    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    # Obtener detalles
    statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
    detalles_db = session.exec(statement).all()
    
    # Construir respuesta
    detalles_respuesta = []
    for det in detalles_db:
        subtotal = det.cantidad * det.precio_unitario
        detalles_respuesta.append({
            "cantidad": det.cantidad,
            "precio_unitario": float(det.precio_unitario),
            "subtotal": float(subtotal)
        })
    
    return VentaResponse(
        id_venta=venta.id_venta,
        id_suc=venta.id_suc,
        id_cliente=venta.id_cliente,
        fecha_hora=venta.fecha_hora,
        total=float(venta.total),
        detalles=detalles_respuesta
    )



@router.put("/{id_venta}")
async def actualizar_venta(
    id_venta: int,
    venta_request: VentaRequest,
    session: Session = Depends(get_session)
):
    if not venta_request.items:
        raise HTTPException(status_code=400, detail="La venta debe contener al menos un item")

    # Verificar que la venta existe
    venta_existente = session.get(Venta, id_venta)
    if not venta_existente:
        raise HTTPException(status_code=404, detail=f"Venta con ID {id_venta} no encontrada")

    # Validar pagos si tipo_servicio es 1
    if venta_request.tipo_servicio == 1:
        if not venta_request.pagos or len(venta_request.pagos) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar al menos un método de pago cuando el tipo de servicio es 1 (para llevar)"
            )

    # Validar cliente solo si tipo_servicio es 2 (domicilio)
    if venta_request.tipo_servicio == 2:
        if not venta_request.id_cliente:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el id_cliente cuando el tipo de servicio es 2 (domicilio)"
            )
        
        cliente = session.get(Cliente, venta_request.id_cliente)
        if not cliente:
            raise HTTPException(
                status_code=404, 
                detail=f"Cliente con ID {venta_request.id_cliente} no encontrado"
            )
        
        # Validar que la dirección existe
        if not venta_request.id_direccion:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el id_direccion cuando el tipo de servicio es 2 (domicilio)"
            )
        
        direccion = session.get(Direccion, venta_request.id_direccion)
        if not direccion:
            raise HTTPException(
                status_code=404, 
                detail=f"Dirección con ID {venta_request.id_direccion} no encontrada"
            )

    # Validar mesa si tipo_servicio es 0 (comer aquí)
    if venta_request.tipo_servicio == 0:
        if venta_request.mesa is None:
            raise HTTPException(
                status_code=400, 
                detail="Debe especificar el número de mesa cuando el tipo de servicio es 0 (comer aquí)"
            )

    # Verificar sucursal
    sucursal = session.get(Sucursal, venta_request.id_suc)
    if not sucursal:
        raise HTTPException(
            status_code=404, 
            detail=f"Sucursal con ID {venta_request.id_suc} no encontrada"
        )

    try:
        # Actualizar datos de la venta
        venta_existente.id_suc = venta_request.id_suc
        venta_existente.mesa = venta_request.mesa if venta_request.tipo_servicio == 0 else None
        venta_existente.total = Decimal(str(venta_request.total))
        venta_existente.comentarios = venta_request.comentarios
        venta_existente.tipo_servicio = venta_request.tipo_servicio
        venta_existente.status = venta_request.status
        venta_existente.nombreClie = venta_request.nombreClie
        
        # Actualizar o crear registro en pDireccion si es domicilio (tipo_servicio = 2)
        if venta_request.tipo_servicio == 2:
            # Buscar si ya existe un registro de domicilio para esta venta
            statement_domicilio = select(pDireccion).where(pDireccion.id_venta == id_venta)
            domicilio_existente = session.exec(statement_domicilio).first()
            
            if domicilio_existente:
                # Actualizar el registro existente
                domicilio_existente.id_clie = venta_request.id_cliente
                domicilio_existente.id_dir = venta_request.id_direccion
            else:
                # Crear nuevo registro
                nuevo_domicilio = pDireccion(
                    id_clie=venta_request.id_cliente,
                    id_dir=venta_request.id_direccion,
                    id_venta=id_venta
                )
                session.add(nuevo_domicilio)
        else:
            # Si cambió el tipo de servicio y ya no es domicilio, eliminar registro de pDireccion si existe
            statement_domicilio = select(pDireccion).where(pDireccion.id_venta == id_venta)
            domicilio_existente = session.exec(statement_domicilio).first()
            if domicilio_existente:
                session.delete(domicilio_existente)
        
        # Manejar pagos si tipo_servicio es 1 (para llevar)
        # Primero eliminar pagos existentes
        statement_pagos = select(Pago).where(Pago.id_venta == id_venta)
        pagos_existentes = session.exec(statement_pagos).all()
        for pago in pagos_existentes:
            session.delete(pago)
        
        # Crear nuevos pagos si tipo_servicio es 1
        pagos_creados = []
        if venta_request.tipo_servicio == 1 and venta_request.pagos:
            for pago_request in venta_request.pagos:
                nuevo_pago = Pago(
                    id_venta=id_venta,
                    id_metpago=pago_request.id_metpago,
                    monto=Decimal(str(pago_request.monto))
                )
                session.add(nuevo_pago)
                pagos_creados.append({
                    "id_metpago": pago_request.id_metpago,
                    "monto": float(pago_request.monto)
                })
        
        session.flush()
        
        # Obtener todos los detalles actuales de la venta
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles_existentes = session.exec(statement).all()
        
        # Separar paquetes de items normales en el request
        items_paquetes = {}  # {id_paquete: item}
        items_normales = []
        
        for item in venta_request.items:
            if item.id_paquete is not None:
                items_paquetes[item.id_paquete] = item
            else:
                items_normales.append(item)
        
        for detalle in detalles_existentes:
            if detalle.id_paquete is not None:
                # Es un paquete - solo actualizar status si cambió
                if detalle.id_paquete in items_paquetes:
                    nuevo_status = items_paquetes[detalle.id_paquete].status
                    if detalle.status != nuevo_status:
                        detalle.status = nuevo_status
                # No hacer nada si el paquete no viene en el request
            else:
                # No es paquete - eliminar físicamente
                session.delete(detalle)
        
        session.flush()
        
        # Crear solo los nuevos items normales (no paquetes)
        for item in items_normales:
            nuevo_detalle = DetalleVenta(
                id_venta=id_venta,
                cantidad=item.cantidad,
                precio_unitario=Decimal(str(item.precio_unitario)),
                status=item.status,
                id_hamb=item.id_hamb,
                id_cos=item.id_cos,
                id_alis=item.id_alis,
                id_spag=item.id_spag,
                id_papa=item.id_papa,
                id_rec=item.id_rec,
                id_barr=item.id_barr,
                id_maris=item.id_maris,
                id_refresco=item.id_refresco,
                id_paquete=item.id_paquete,
                detalle_paquete=item.detalle_paquete,
                id_magno=item.id_magno,
                id_pizza=item.id_pizza
            )
            session.add(nuevo_detalle)

        session.commit()
        
        respuesta = {
            "Mensaje": "Venta actualizada exitosamente",
            "id_venta": id_venta,
            "tipo_servicio": venta_existente.tipo_servicio
        }
        
        # Agregar información específica según el tipo de servicio
        if venta_request.tipo_servicio == 0:
            respuesta["mesa"] = venta_existente.mesa
        elif venta_request.tipo_servicio == 1:
            respuesta["pagos_registrados"] = pagos_creados
            respuesta["numero_pagos"] = len(pagos_creados)
        elif venta_request.tipo_servicio == 2:
            respuesta["id_cliente"] = venta_request.id_cliente
            respuesta["id_direccion"] = venta_request.id_direccion
        
        if venta_request.nombreClie:
            respuesta["nombreClie"] = venta_request.nombreClie
        
        return respuesta

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la venta: {str(e)}")



@router.delete("/{id_venta}")
async def eliminar_venta(
    id_venta: int,
    session: Session = Depends(get_session)
):
    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    try:
        statement = select(DetalleVenta).where(DetalleVenta.id_venta == id_venta)
        detalles = session.exec(statement).all()
        for detalle in detalles:
            session.delete(detalle)
        
        # Eliminar venta
        session.delete(venta)
        session.commit()
        
        return {"Message":"Venta eliminada exitosamente"}
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar la venta: {str(e)}")



@router.get("/")
async def listar_ventas(
    session: Session = Depends(get_session),
    filtro: str = "hoy",
    status: Optional[int] = None,
    id_suc: Optional[int] = None,
):
    try:
        # Construir query base
        statement = select(Venta).order_by(Venta.fecha_hora.asc())

        if filtro == "hoy":
            hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            hoy_fin = hoy_inicio + timedelta(days=1)
            statement = statement.where(
                Venta.fecha_hora >= hoy_inicio,
                Venta.fecha_hora < hoy_fin
            )

        if status is not None:
            statement = statement.where(Venta.status == status)

        if id_suc:
            statement = statement.where(Venta.id_suc == id_suc)

        ventas = session.exec(statement).all()

        ventas_resumidas = []
        for venta in ventas:
            # Obtener cliente
            cliente = session.get(Cliente, venta.id_cliente)
            nombre_cliente = cliente.nombre if cliente else "Desconocido"

            # Obtener sucursal
            sucursal = session.get(Sucursal, venta.id_suc)
            nombre_sucursal = sucursal.nombre if sucursal else "Desconocida"

            # Contar items
            statement_detalles = select(DetalleVenta).where(DetalleVenta.id_venta == venta.id_venta)
            detalles = session.exec(statement_detalles).all()
            total_items = sum(det.cantidad for det in detalles)

            ventas_resumidas.append({
                "id_venta": venta.id_venta,
                "fecha_hora": venta.fecha_hora,
                "cliente": nombre_cliente,
                "sucursal": nombre_sucursal,
                "status": venta.status,
                "total": float(venta.total),
                "cantidad_items": total_items,
                "cantidad_productos": len(detalles)
            })

        return {
            "ventas": ventas_resumidas,
            "total": len(ventas_resumidas),
            "filtro_aplicado": filtro,
            "status_filtrado": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")



@router.patch("/{id_venta}/toggle-preparacion")
async def toggle_preparacion(
    id_venta: int,
    session: Session = Depends(get_session)
):

    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    try:
        if venta.status == 0:
            venta.status = 1
            mensaje = "Pedido marcado como 'Preparando'"
        elif venta.status == 1:
            venta.status = 0
            mensaje = "Pedido regresado a 'Esperando'"
        else:
            raise HTTPException(
                status_code=400,
                detail="No se puede cambiar el estado. El pedido ya está completado."
            )
        
        session.add(venta)
        session.commit()
        session.refresh(venta)
        
        return {
            "message": mensaje,
            "id_venta": venta.id_venta,
            "nuevo_status": venta.status,
            "status_texto": {0: "Esperando", 1: "Preparando"}[venta.status]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar status: {str(e)}")



@router.patch("/{id_venta}/completar")
async def completar_pedido(
    id_venta: int,
    session: Session = Depends(get_session)
):

    venta = session.get(Venta, id_venta)
    if not venta:
        raise HTTPException(status_code=404, detail=f"Venta {id_venta} no encontrada")
    
    try:
        if venta.status != 1:
            raise HTTPException(
                status_code=400,
                detail=f"Solo se pueden completar pedidos en preparación. Estado actual: {venta.status}"
            )
        
        # Cambiar el estado de la venta
        venta.status = 2
        session.add(venta)

        # Cambiar el estado de todos los detalles de venta asociados
        stmt = (
            update(DetalleVenta)
            .where(DetalleVenta.id_venta == id_venta)
            .values(status=2)
        )
        session.execute(stmt)

        session.commit()
        session.refresh(venta)
        
        return {
            "message": "Pedido completado exitosamente",
            "id_venta": venta.id_venta,
            "nuevo_status": 2,
            "status_texto": "Completado"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al completar pedido: {str(e)}")




