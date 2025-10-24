from sqlmodel import SQLModel
import sys

# Importar modelos
from app.models.ventaModel import Venta
from app.models.detallesModel import DetalleVenta

# Forzar actualización de forward references
if sys.version_info >= (3, 10):
    Venta.model_rebuild(force=True)
    DetalleVenta.model_rebuild(force=True)
else:
    Venta.model_rebuild()
    DetalleVenta.model_rebuild()