from pydantic import BaseModel
from typing import List
import cv2
from imutils.video.webcamvideostream import WebcamVideoStream
class Student():
    def __init__(self, **kwargs):
        self.success = False
        self.res_log = []
        for key, value in kwargs.items():
            setattr(self, key, value)

k={"success":True,"res_log":[1,3]}

class UserResponse(BaseModel):
    exists:bool=True
    grouped:bool=False
    user_details:List=[]

capture = WebcamVideoStream(src=0).start()
cv2.imwrite("temp.jpeg",capture.read())


if __name__ == "__main__":
    print("wow")