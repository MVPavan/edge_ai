from redis import Redis
from FRModule.FRCore.fr_config import RedisDB
from loguru import logger

redis_conn = Redis(
    host=RedisDB.REDIS_SERVER, port=RedisDB.REDIS_PORT, db=RedisDB.REDIS_DB
)

if redis_conn.ping() == True:
    logger.info("Model Container Established connection with redis!!")
else:
    logger.info("Model Container Redis connection failed!!")
