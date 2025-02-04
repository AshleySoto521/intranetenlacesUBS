from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+pg8000://USER:PASSWORD@localhost:5432/directorios_db"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL, echo=True)

# Crear una clase base para los modelos
Base = declarative_base()

# Crear sesión
Session = sessionmaker(bind=engine)

def get_engine():
    return engine
