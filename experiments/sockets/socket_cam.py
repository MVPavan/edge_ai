from __future__ import print_function
import websocket
import time, json
from numpy import random
import cv2
rtsp_link = "rtsp:/192.168.0.143:5554/playlist.m3u"
groupUUID = "bce46197f396486aa6929697f5bb7633"

import numpy as np
import base64
import sys
import cv2


def decodeCVIMG(frame,):
    frame = base64.b64decode(frame)
    frame = np.fromstring(frame, dtype=np.uint8)
    frame = cv2.imdecode(frame, 1)
    return frame



if __name__ == "__main__":
    websocket.enableTrace(True)
    num = random.randint(100, 100000)
    ws = websocket.create_connection(
        url = "ws://localhost:8000/api/v1/face/ws/stream",
        # options = {
        #     "item_id" : num,
        #     "q" : "Heyyy"
        # }
        )
    result = ws.recv()
    print("Received '%s'" % result)
    if result:
        result = json.loads(result)
        result["cam_link"] = rtsp_link
        ws.send(json.dumps(result))
        count=0
        ts = time.time()
        while True:
            print("Receiving...")
            result = ws.recv()
            # print("Received '%s'" % result)
            # print("wow")
            if result == "stop":
                break
            # result=json.loads(result)
            frame = decodeCVIMG(result)#.reshape(640,480,3)
            cv2.imshow("Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            # print("EId Scores:", result["res_log"]["eid_scores"])
            count = count+1
            print("FPS: ",count/(time.time()-ts))


    ws.close()