import os
from enum import Enum
# from dotenv import load_dotenv
from starlette.datastructures import CommaSeparatedStrings, Secret
from databases import DatabaseURL

API_V1_STR = "/api/v1"
# load_dotenv(".env")

PROJECT_NAME = os.getenv("PROJECT_NAME", "HON Face Recognition")
# ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))
SECRET_KEY = Secret(os.getenv("SECRET_KEY", "secret key for project"))


# from imutils.video import WebcamVideoStream
# capture = WebcamVideoStream(src=0).start()

############################################################################################


POSTGRES_URL = os.getenv("POSTGRES_URL", "")  # deploying without docker-compose
if not POSTGRES_URL:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER = os.getenv("POSTGRES_USER", "pavan_pgdb")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "FR_SERVER")

    POSTGRES_URL = DatabaseURL(
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
else:
    POSTGRES_URL = DatabaseURL(POSTGRES_URL)

# print(str(POSTGRES_URL))
############################################################################################

MAX_CONNECTIONS_COUNT = int(os.getenv("MAX_CONNECTIONS_COUNT", 50))
MIN_CONNECTIONS_COUNT = int(os.getenv("MIN_CONNECTIONS_COUNT", 20))
MONGODB_URL = os.getenv("MONGODB_URL", "")  # deploying without docker-compose
if not MONGODB_URL:
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "pavan_mdb")
    MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password")
    MONGO_DB = os.getenv("MONGO_INITDB_DATABASE", "FR_SERVER")

    MONGODB_URL = DatabaseURL(
        f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"
    )
else:
    MONGODB_URL = DatabaseURL(MONGODB_URL)

# print(str(MONGODB_URL))

############################################################################################
REDIS_SERVER = os.getenv("REDIS_SERVER", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_QUEUES = os.getenv("REDIS_QUEUES", ["low", "default", "high"])
REDIS_DB = os.getenv("REDIS_DB", 0)

############################################################################################

MINIO_HOST = os.getenv("MINIO_HOST", "localhost")
MINIO_PORT = os.getenv("MINIO_PORT", 9000)
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
# MINIO_FR_TAGS = [".jpg",".png"]
MINIO_HOST_URL = f"{MINIO_HOST}:{MINIO_PORT}"

############################################################################################
class FrBuckets(str, Enum):
    logs = "frlogs"
    FRDB = "frdb"
    models = "frmodels"

class FRQueues(str, Enum):
    FRInQ = os.getenv("FRInQ", "FRInQ")
    FROutQ = os.getenv("FROutQ", "FROutQ")
    FROutH = os.getenv("FROutH", "FROutH")
    FRCInQ = os.getenv("FRCInQ", "FRCInQ")
    FRCOutH = os.getenv("FRCOutH", "FRCOutH")
    FRCInH = os.getenv("FRCInH", "FRCInH")

REDIS_WORKERS = {
    FrBuckets.logs: f"fr_{FrBuckets.logs}",
    FrBuckets.FRDB: f"fr_{FrBuckets.FRDB}",
    FrBuckets.models: f"fr_{FrBuckets.models}",
}

MINIO_NOTIFICATION_QUEUES = {
    FrBuckets.logs: f"fr_{FrBuckets.logs}_Q",
    FrBuckets.FRDB: f"fr_{FrBuckets.FRDB}_Q",
    FrBuckets.models: f"fr_{FrBuckets.models}_Q",
}