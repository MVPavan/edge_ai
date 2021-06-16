from app.db.utils.minio_py_client import MinioClient
from minio.error import ResponseError
from rq import Queue as RJQ
from app.core.config import (
    MINIO_HOST_URL,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_NOTIFICATION_QUEUES,
)
from loguru import logger

minio_client = MinioClient(
    host=MINIO_HOST_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)
[print(b.name) for b in minio_client.list_buckets()]


def get_register_events():
    events = minio_client._minio_client.listen_bucket_notification(
        bucket_name="face_register",
        prefix="",
        suffix="",
        events=["s3:ObjectCreated:*", "s3:ObjectRemoved:*", "s3:ObjectAccessed:*"],
    )
    for event in events:
        image_path = event["Records"][0]["s3"]["object"]["key"].replace("%2F", "/")
        [org, team, user, fimage] = image_path.split("/")
        event_log = {
            "Bucket Name": event["Records"][0]["s3"]["bucket"]["name"],
            "organization": org,
            "team": team,
            "user": user,
            "image": fimage,
            "eTag": event["Records"][0]["s3"]["object"]["eTag"],
        }
        logger.info(str(event_log))
        print(event_log)


def get_logs_events():
    events = minio_client._minio_client.listen_bucket_notification(
        bucket_name="logs",
        prefix="",
        suffix="",
        events=["s3:ObjectCreated:*", "s3:ObjectRemoved:*", "s3:ObjectAccessed:*"],
    )
    for event in events:
        image_path = event["Records"][0]["s3"]["object"]["key"].replace("%2F", "/")
        [org, team, fimage] = image_path.split("/")
        event_log = {
            "Bucket Name": event["Records"][0]["s3"]["bucket"]["name"],
            "organization": org,
            "team": team,
            "image": fimage,
            "eTag": event["Records"][0]["s3"]["object"]["eTag"],
        }
        logger.info(str(event_log))
        print(event_log)
