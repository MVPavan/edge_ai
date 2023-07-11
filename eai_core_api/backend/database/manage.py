from imports import (
    SQLModel, create_engine, Session, logger
)

from config import POSTGRES_URL, POSTGRES_URL_LOCAL

engine = create_engine(
    url=POSTGRES_URL,
    # connect_args={"check_same_thread": False}
)

 
def load_engine_local():
    global engine
    engine = create_engine(
        url=POSTGRES_URL_LOCAL,
    )


def create_db():
    try:
        SQLModel.metadata.create_all(engine)
    except:
        logger.error(f"Error: Could not connect to {POSTGRES_URL}")
        logger.info(f"Trying to connect to {POSTGRES_URL_LOCAL}")
        try:
            load_engine_local()
            SQLModel.metadata.create_all(engine)
        except:
            logger.error(f"Error: Could not connect to {POSTGRES_URL_LOCAL}")
            exit()


def get_pgdb_session():
    with Session(engine) as session:
        yield session