# make sure all SQL Alchemy models are imported before initializing DB
# otherwise, SQL Alchemy might fail to initialize properly relationships
from fastapi import Depends
from .pgdb_utils import connect_to_pgdb, LocalSession, Session, Base
from .mdb_utils import (
    connect_to_mongo,
    MongoClient,
    mdb,
    close_mongo_connection,
    get_mdb_worker,
)
from .minio_utils import minio_conn
from app.db.utils.strings import DBSessions 
from app.db.utils.redis_utils import redis_conn as rc


def get_pgdb() -> Session:
    try:
        db = LocalSession()
        yield db
    finally:
        # print("pgdb closed !!!!")
        db.close()

def get_mdb() -> MongoClient:
    return mdb.client

def get_minio():
    return minio_conn


def get_rpubsub():
    try:
        p = rc.pubsub(ignore_subscribe_messages=True)
        p.subscribe('FrChannel')
        yield p
    finally:
        # print("closed pubsub")
        p.close()


def get_db_sessions(
    pgdbs = Depends(get_pgdb, use_cache=False),
    mdbs = Depends(get_mdb),
    mios = Depends(get_minio),
    # rpubsub = Depends(get_rpubsub, use_cache=False)
):
    return DBSessions(**{
        "pgdbs": pgdbs,
        "mdbs": mdbs,
        "mios": mios,
        # "rpubsub": rpubsub
    })
