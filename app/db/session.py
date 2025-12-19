from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

from app.models import (empleadoModel, 
                        clienteModel, 
                        magnoModel, 
                        sucursalModel, 
                        ventaModel, 
                        detallesModel, 
                        pagosModel, 
                        gastosModel, 
                        alitasModel, 
                        barraModel, 
                        categoriaModel, 
                        costillasModel, 
                        especialidadModel, 
                        hamburguesasModel, 
                        papasModel, 
                        paquetesModel, 
                        mariscosModel, 
                        rectangularModel, 
                        refrescosModel, 
                        spaguettyModel, 
                        tamanosPizzasModel, 
                        tamanosRefrescosModel,
                        permisosModel,
                        pizzasModel,
                        DireccionesModel,
                        pDireccionModel,
                        cajaModel,
                        pEspecialModel)


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
