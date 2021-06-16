import numpy as np
import base64
import sys
import cv2


IMAGE_DTYPE = np.uint8

def encodeCVIMG(frame):
    frame = cv2.resize(frame,(640,480))
    encoded, frame = cv2.imencode('.jpg', frame)
    return base64.b64encode(frame)
        

def encodeIMG(fr_img):
    return base64.b64encode(fr_img).decode("utf-8")
    # return base64.b64encode(fr_img).decode("utf-8")


def decodeIMG(fr_img, dtype, name=""):
    fr_img = np.frombuffer(base64.b64decode(fr_img.encode("utf-8")), dtype=IMAGE_DTYPE)
    # fr_img=np.fromstring(base64.b64decode(fr_img.encode('utf-8')),dtype=IMAGE_DTYPE)
    fr_img = cv2.imdecode(fr_img, 1)
    # cv2.imwrite(f"./{name}", fr_img)
    return fr_img


# image2 = np.asarray(bytearray(file.file.read()), dtype="uint8")
# image2 = cv2.imdecode(image2, cv2.IMREAD_COLOR)
# cv2.imwrite("temp2.jpeg",image2)

# cv2.imdecode(np.fromstring(file.file.read(), np.uint8), 1)
# cv2.imwrite("temp2.jpeg",image2)

"""
https://www.pyimagesearch.com/2018/02/05/deep-learning-production-keras-redis-flask-apache/
https://www.pyimagesearch.com/2015/05/11/creating-a-face-detection-api-with-python-and-opencv-in-just-5-minutes/
https://gist.github.com/gachiemchiep/52f3255a81c907461c2c7ced6ede367a
https://stackoverflow.com/questions/15225053/how-to-store-an-image-into-redis-using-python-pil
https://stackoverflow.com/questions/47515243/reading-image-file-file-storage-object-using-cv2
https://stackoverflow.com/questions/17170752/python-opencv-load-image-from-byte-string
https://stackoverflow.com/questions/40928205/python-opencv-image-to-byte-string-for-json-transfer/58406222#58406222
"""
