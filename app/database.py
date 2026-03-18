from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.auth.models import Base
from app.config import settings

engine = create_engine(
    settings.postgres_url,
    pool_pre_ping=True,
    future=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
