from pydantic import BaseModel


class createMariscos(BaseModel):
    nombre: str
    descripcion: str
    id_tamañop: int
    id_cat: int
    
class readMariscos(BaseModel):
    id_maris: int
    nombre: str
    descripcion: str
    id_tamañop: int
    id_cat: int
    
class readMariscosOut(BaseModel):
    id_maris: int
    nombre: str
    descripcion: str
    tamaño: str
    categoria: str
    