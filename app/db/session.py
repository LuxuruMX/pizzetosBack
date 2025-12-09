from sqlmodel import SQLModel, create_engine, Session
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
                        movimientoCajaModel)

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/pizzetos_db"


engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
