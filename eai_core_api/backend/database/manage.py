from imports import (
    SQLModel, create_engine, Session
)

from config import POSTGRES_URL

engine = create_engine(
    url=POSTGRES_URL,
    # connect_args={"check_same_thread": False}
)


def create_db():
    SQLModel.metadata.create_all(engine)


def get_pgdb_session():
    with Session(engine) as session:
        yield session