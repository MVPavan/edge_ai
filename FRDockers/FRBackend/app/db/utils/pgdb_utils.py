from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from app.core.config import POSTGRES_URL
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from loguru import logger
from starlette.requests import Request

# from app.core import config

# POSTGRES_URL = 'postgresql://pavan:password@localhost/pavan'

engine = create_engine(str(POSTGRES_URL), pool_pre_ping=True, pool_size=20, max_overflow=100)
LocalSession = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
# LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class CustomBase(object):
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=CustomBase)

# make sure all SQL Alchemy models are imported before initializing DB
# otherwise, SQL Alchemy might fail to initialize properly relationships
def connect_to_pgdb():
    logger.info("Initializing postgres database .....")
    Base.metadata.create_all(bind=engine)
    logger.info("Postgres database Initialization successful!")


# def close_pgdb_session():
#     logger.info("Closing postgres database connection.....")
#     pgdb_session.close()
#     logger.info("Postgres database connection closing successful!")
