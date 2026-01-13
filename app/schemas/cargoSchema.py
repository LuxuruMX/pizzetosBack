from pydantic import BaseModel, Field

class createCargo(BaseModel):
    nombre: str = Field(min_length=5, max_length=100)

class readCargo(BaseModel):
    id_ca: int
    nombre: str
    class config:
        from_attributes = True