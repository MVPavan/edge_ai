from redis import Redis, StrictRedis
from rq import Queue as RJQ
from app.core.config import REDIS_QUEUES, REDIS_SERVER, REDIS_PORT, REDIS_DB
from loguru import logger
from app.core.config import FrBuckets, MINIO_NOTIFICATION_QUEUES


redis_conn = StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=REDIS_DB)

if redis_conn.ping() == True:
    logger.info("Established connection with redis!!")
else:
    logger.info("Redis connection failed!!")

RJQ_Register = RJQ(MINIO_NOTIFICATION_QUEUES[FrBuckets.FRDB], connection=redis_conn)
RJQ_Logs = RJQ(MINIO_NOTIFICATION_QUEUES[FrBuckets.logs], connection=redis_conn)
