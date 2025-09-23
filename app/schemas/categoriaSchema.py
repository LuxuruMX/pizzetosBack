from pydantic import BaseModel, Field

class createCategoria(BaseModel):
    descripcion: str
    
class readCategoria(BaseModel):
    id_cat: int
    descripcion: str

    class Config:
        orm_mode = True