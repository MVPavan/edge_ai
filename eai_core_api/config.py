import os
from dotenv import load_dotenv
from pathlib import Path
from starlette.datastructures import CommaSeparatedStrings, Secret

API_V1_STR = "/edgeai/core_api/v1"

# Load env file
env_path = Path(__file__).parent / 'docker/.env.eai_core_api'
load_dotenv(env_path.as_posix())

PROJECT_NAME = os.getenv("PROJECT_NAME", "EdgeAI Server")
# ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))
SECRET_KEY = Secret(os.getenv("SECRET_KEY", "secret key for project"))

LOCAL_HOST = "localhost"

############################################################################################
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8090))

############################################################################################

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "pgdb_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "pgdb_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "edgeai_pgdb")

POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
POSTGRES_URL_LOCAL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{LOCAL_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    

# print(str(POSTGRES_URL))
############################################################################################

REDIS_SERVER = os.getenv("REDIS_SERVER", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_QUEUES = os.getenv("REDIS_QUEUES", ["low", "default", "high"])
REDIS_DB = os.getenv("REDIS_DB", 0)
REDIS_URL = f"redis://{REDIS_SERVER}:{REDIS_PORT}/{REDIS_DB}"

############################################################################################

RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "rabbitmq_user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_DEFAULT_PASS", "rabbitmq_password")
RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@localhost:5672/"
# RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@localhost:15672/"

############################################################################################

MINIO_HOST = os.getenv("MINIO_HOST", "localhost")
MINIO_PORT = os.getenv("MINIO_PORT", 9000)
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
# MINIO_FR_TAGS = [".jpg",".png"]
MINIO_HOST_URL = f"{MINIO_HOST}:{MINIO_PORT}"

############################################################################################