from sqlmodel import SQLModel, Session, create_engine
from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, echo=False, pool_pre_ping=True)


    # Creates tables from SQLModel metadata once models exist.
    # Right now there are no models, so this is a no-op but proves the
    # DB connection itself works.

def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session