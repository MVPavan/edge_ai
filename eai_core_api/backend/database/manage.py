from imports import (
    SQLModel, create_engine, Session
)

from config import POSTGRES_URL, POSTGRES_URL_LOCAL

try:
    engine = create_engine(
        url=POSTGRES_URL,
        # connect_args={"check_same_thread": False}
    )
except:
    print(f"Error: Could not connect to {POSTGRES_URL}")
    print(f"Trying to connect to {POSTGRES_URL_LOCAL}")
    try:
        engine = create_engine(
            url=POSTGRES_URL_LOCAL,
        )
    except:
        print(f"Error: Could not connect to {POSTGRES_URL_LOCAL}")
        exit()

def create_db():
    SQLModel.metadata.create_all(engine)


def get_pgdb_session():
    with Session(engine) as session:
        yield session