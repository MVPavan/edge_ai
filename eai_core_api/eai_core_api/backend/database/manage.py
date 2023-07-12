from eai_core_api.imports import (
    SQLModel, create_engine, Session, text,
    logger
)

from eai_core_api.config import POSTGRES_URL, POSTGRES_URL_LOCAL


def create_postgres_engine():
    def get_engine(DB_URL):
        engine = create_engine(url=DB_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info(f"Connected to postrgesql database: {DB_URL}")
        return engine
    
    try:
        engine = get_engine(POSTGRES_URL)
    except Exception as e:
        logger.error(f"Error Connecting Postgres DB usign {POSTGRES_URL}")

        try:
            engine = get_engine(POSTGRES_URL_LOCAL)
        except Exception as e:
            logger.error(f"Error Connecting Postgres DB usign {POSTGRES_URL_LOCAL} ")
            exit()
    return engine

engine = create_postgres_engine()

def create_db():
    SQLModel.metadata.create_all(engine)

def get_pgdb_session():
    with Session(engine) as session:
        yield session