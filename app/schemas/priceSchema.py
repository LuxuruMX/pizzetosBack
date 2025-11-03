from pydantic import BaseModel
from decimal import Decimal

class priceHamburguesa(BaseModel):
    id_hamb: int
    nombre: str
    precio: Decimal
    
class PriceAlita(BaseModel):
    id_alis: int
    nombre: str
    precio: Decimal
    
class PriceCostilla(BaseModel):
    id_cos: int
    nombre: str
    precio: Decimal
    
class PriceSpaghetti(BaseModel):
    id_spag: int
    nombre: str
    precio: Decimal
    
class PricePapas(BaseModel):
    id_papa: int
    nombre: str
    precio: Decimal
    
class PriceRectangular(BaseModel):
    id_rec: int
    nombre: str
    precio: Decimal

class PriceBarra(BaseModel):
    id_barr: int
    nombre: str
    precio: Decimal

class PriceMarisco(BaseModel):
    id_maris: int
    nombre: str
    precio: Decimal

class PriceRefresco(BaseModel):
    id_refresco: int
    nombre: str
    precio: Decimal
    tamano: str
    
class PricePaquete1(BaseModel):
    id_paquete1: int
    nombre: str
    precio: Decimal
    
class PricePaquete2(BaseModel):
    id_paquete2: int
    nombre: str
    precio: Decimal

class PricePaquete3(BaseModel):
    id_paquete3: int
    nombre: str
    precio: Decimal
    
class PriceMagno(BaseModel):
    id_magno: int
    nombre: str
    precio: Decimal

class PricePizza(BaseModel):
    id_pizza: int
    nombre: str
    precio: Decimal
    tamano: str