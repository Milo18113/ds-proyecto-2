import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lee la URL de conexión desde variables de entorno.
# Si no existe usa una URL por defecto.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fintech_db"
)

# Engine: conexión principal a la base de datos.
engine = create_engine(DATABASE_URL, echo=False)

# SessionLocal: fábrica de sesiones. 
# Cada request de la API abrirá una sesión y la cerrará al terminar.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: todas las clases ORM (modelos) heredan de esta clase.
# SQLAlchemy la usa para saber qué tablas crear.
Base = declarative_base()


def get_db():
    """
    Dependency para FastAPI.
    Abre una sesión de BD, la entrega al endpoint,
    y la cierra cuando termina (incluso si hay error).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crea todas las tablas en la BD basándose en los modelos
    que heredan de Base. Útil para desarrollo/inicio.
    """
    Base.metadata.create_all(bind=engine)