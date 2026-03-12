from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session

from library.config import settings
from .models import Base


engine = create_engine(
    url=URL.create(
        drivername="postgresql+psycopg2",
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
    ),
    # echo=True
)

SessionLocal = sessionmaker(bind=engine)


def get_session() -> Session:
    return SessionLocal()


def init_db():
    Base.metadata.create_all(bind=engine)
