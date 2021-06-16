# from minio_py_client import MinioClient
# from minio.error import ResponseError
# client = MinioClient("127.0.0.1:9000",access_key="minio", secret_key="minio123",secure=False )
# class FrBuckets:
#     logs='FRlogs'
#     FRDB='FRDB'
#     models='FRmodels'


# for b in client.list_buckets():
#     print(b.name)


# # notification_1 = {
# #     'QueueConfigurations': [
# #         {
# #             'Id': '1',
# #             'Arn': 'arn:minio:sqs::queue:redis',
# #             'Events': ['s3:ObjectCreated:*',
# #                     's3:ObjectRemoved:*',
# #             ]
# #         },
# #         {
# #             'Id': '2',
# #             'Arn': 'arn:minio:sqs::hash:redis',
# #             'Events': ['s3:ObjectCreated:*',
# #                     's3:ObjectRemoved:*',

# #             ]
# #         }

# #     ]
# # }


# # try:
# #     client._minio_client.set_bucket_notification('images', notification_1)
# # except ResponseError as err:
# #     # handle error response from service.
# #     print(err)
# # except (ArgumentError, TypeError) as err:
# #     # should happen only during development. Fix the notification argument
# #     print(err)


# # notif = client._minio_client.get_bucket_notification('images')
# # event_log=[]
# # def get_events():

# #     # events = client._minio_client.listen_bucket_notification('images', 'test1/',
# #     #                                         ['s3:ObjectCreated:*',
# #     #                                             's3:ObjectRemoved:*',
# #     #                                             's3:ObjectAccessed:*'])
# #     events = client._minio_client.listen_bucket_notification(bucket_name="images",
# #                                                             prefix="",
# #                                                             suffix="",
# #                                                             events=['s3:ObjectCreated:*',
# #                                                                     's3:ObjectRemoved:*',
# #                                                                     's3:ObjectAccessed:*']
# #                                                             )
# #     for event in events:
# #         event_log.append(event)
# #         print(event)


# # print(notif)
# # get_events()


# from redis import Redis

# rdb = Redis(host="127.0.0.1", port=6379, db=0)

# print("redis_operations")


from threading import Thread
import requests
import time
import io
import cv2
from PIL import Image
from imutils.video import WebcamVideoStream

capture = WebcamVideoStream(src=0).start()

url = "http://localhost:8000/api/v1/honfr_v1/register_user"
NUM_REQUESTS = 500
SLEEP_COUNT = 0.05


def call_predict_endpoint(n=0):
    # image = open(IMAGE_PATH, "rb").read()
    payload = {
        "eid": "h242998_24",
        "name": "pavan",
        "groupUUID": "348311da-a2b9-4064-8a71-f5eafdb6b743",
    }
    frame = capture.read()
    frame_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(frame_im)
    stream = io.BytesIO()
    pil_im.save(stream, format="JPEG")
    stream.seek(0)
    img_for_post = stream.read()

    files = [
        ("input_files", open("/home/pavanmv/Pictures/h242998.jpeg", "rb")),
        ("input_files", img_for_post),
    ]

    headers = {
        "Content-Type": "multipart/form-data; boundary=--------------------------500738441943852772649857"
    }

    response = requests.request("POST", url, data=payload, files=files)

    print(response.text.encode("utf8"))

    # ensure the request was sucessful


# if r["success"]:
# 	print("[INFO] thread {} OK".format(n))
# # otherwise, the request failed
# else:
# 	print("[INFO] thread {} FAILED".format(n))


# loop over the number of threads
# for i in range(0, NUM_REQUESTS):
# 	# start a new thread to call the API
# 	t = Thread(target=call_predict_endpoint, args=(i,))
# 	t.daemon = True
# 	t.start()
# 	time.sleep(SLEEP_COUNT)
# insert a long sleep so we can wait until the server is finished
# processing the images
# time.sleep(300)

# import io
# output = io.StringIO()
# im = Image.open("/home/cwgem/Pictures/portrait.png")
# im.save(output, format=im.format)

if __name__ == "__main__":
    call_predict_endpoint()
