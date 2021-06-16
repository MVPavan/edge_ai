from pymongo import MongoClient
from app.core.config import MONGODB_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT
from loguru import logger


class MongoDataBase:
    client: MongoClient = None


mdb = MongoDataBase()


def connect_to_mongo():
    logger.info("Connecting to Mongo database .....")
    mdb.client = MongoClient(
        str(MONGODB_URL),
        maxPoolSize=MAX_CONNECTIONS_COUNT,
        minPoolSize=MIN_CONNECTIONS_COUNT,
    )
    logger.info("Connection to MongoDB established !")


def close_mongo_connection():
    logger.info("Clossing connection to Mongo database .....")
    mdb.client.close()
    logger.info("Connection to Mongo database closed !")


def get_mdb_worker():
    mdb_worker = MongoClient(
        str(MONGODB_URL),
        maxPoolSize=MAX_CONNECTIONS_COUNT,
        minPoolSize=MIN_CONNECTIONS_COUNT,
    )

    return mdb_worker
