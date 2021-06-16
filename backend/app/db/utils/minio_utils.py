from .minio_py_client import MinioClient
from app.core.config import (
    MINIO_HOST_URL,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    FrBuckets,
)


def check_fr_buckets(minio_conn):
    bucket_list = [b.name for b in minio_conn.list_buckets()]
    if not FrBuckets.FRDB in bucket_list:
        res = minio_conn.make_bucket(FrBuckets.FRDB)
        if res.success:
            print("Created Bucket {}".format(res.response))
        else:
            print("Error creating {} bucket".format(res.response))

    if not FrBuckets.logs in bucket_list:
        res = minio_conn.make_bucket(FrBuckets.logs)
        if res.success:
            print("Created Bucket {}".format(res.response))
        else:
            print("Error creating {} bucket".format(res.response))

    if not FrBuckets.models in bucket_list:
        res = minio_conn.make_bucket(FrBuckets.models)
        if res.success:
            print("Created Bucket {}".format(res.response))
        else:
            print("Error creating {} bucket".format(res.response))


minio_conn = MinioClient(MINIO_HOST_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
check_fr_buckets(minio_conn)
