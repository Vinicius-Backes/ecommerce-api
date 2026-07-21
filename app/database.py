from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency do FastAPI que fornece uma sessão de banco de dados
    e garante que ela seja fechada ao final da requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()