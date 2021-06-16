

# https://www.pyimagesearch.com/2018/02/05/deep-learning-production-keras-redis-flask-apache/

from threading import Thread
import requests
import time
import io
import cv2
from PIL import Image
from imutils.video import WebcamVideoStream
import numpy as np
# capture = WebcamVideoStream(src=0).start()

url = "http://localhost:8000/api/v1/honfr_v1/register_user"
NUM_REQUESTS = 50
SLEEP_COUNT = 0.05
passed_count = 0
failed_count = 0


def call_predict_endpoint(n=0):
    # image = open(IMAGE_PATH, "rb").read()
    payload = {
        "eid": "h242998_{}".format(np.random.randint(100,1000000)+n),
        "name": "pavan",
        "groupUUID": "3c55781d04f14a2bbdd676cbadcb0288",
    }
    
    ################### capture code ####################
    # frame = capture.read()
    # frame_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # pil_im = Image.fromarray(frame_im)
    # stream = io.BytesIO()
    # pil_im.save(stream, format="JPEG")
    # stream.seek(0)
    # img_for_post = stream.read()

    ################### 
    fimage = "/home/pavanmv/Pavan/HW/FR/honfr/Face_DB/PictureBase/HW/e178187_3054_unknown/e178187.jpeg"
    files = [
        ("input_files", open(fimage, "rb")),
        # ("input_files", img_for_post),
    ]
    headers = {
        "Content-Type": "multipart/form-data; boundary=--------------------------500738441943852772649857"
    }
    response = requests.request("POST", url, data=payload, files=files)
    # print(response.text.encode("utf8"))
    # ensure the request was sucessful
    if response.ok:
        print("thread {} OK".format(n))
    else:
        print(" thread {} FAILED".format(n))
    
    # if not response.ok:
    #     print(" thread {} FAILED".format(n))


# import io
# output = io.StringIO()
# im = Image.open("/home/cwgem/Pictures/portrait.png")
# im.save(output, format=im.format)

if __name__ == "__main__":
    # call_predict_endpoint()

    # loop over the number of threads
    tt=time.time()
    for i in range(0, NUM_REQUESTS):
    	# start a new thread to call the API
    	t = Thread(target=call_predict_endpoint, args=(i,))
    	t.daemon = True
    	t.start()
    	time.sleep(SLEEP_COUNT)
    # insert a long sleep so we can wait until the server is finished
    # processing the images
    print("time taken:",time.time()-tt)
    time.sleep(50)
