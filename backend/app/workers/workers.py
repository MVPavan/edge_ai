import os
from rq import Worker, Queue, Connection
from app.core.config import FrBuckets, MINIO_NOTIFICATION_QUEUES, REDIS_WORKERS
from app.db.utils.redis_utils import redis_conn
from .worker_manager import RJQ_Register, RJQ_Logs


def spawn_register_worker(name=REDIS_WORKERS[FrBuckets.FRDB]):
    with Connection(redis_conn):
        worker = Worker([RJQ_Register], name=REDIS_WORKERS[FrBuckets.FRDB])
        worker.work()
        print("awesome")


def spawn_logs_worker(name=REDIS_WORKERS[FrBuckets.logs]):
    with Connection(redis_conn):
        worker = Worker([RJQ_Logs], name=REDIS_WORKERS[FrBuckets.logs])
        worker.work()
