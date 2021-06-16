from __future__ import print_function
import websocket
import time, json
import numpy as np
import cv2
rtsp_link = "rtsp:/192.168.0.143:5554/playlist.m3u"
groupUUID = "8a5728a6900f4c798af15247c2b4e95c"
res = "/home/pavanmv/Pavan/HW/FR/FR_MS/Result"

if __name__ == "__main__":
    websocket.enableTrace(True)
    # num = np.random.randint(100, 100000)
    ws = websocket.create_connection(
        url = "ws://localhost:8000/api/v1/face/ws/infer",
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
        result["mask_detection"] = True
        result["groupUUID"] = groupUUID
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
            result=json.loads(result)
            print("EId Scores:", result["res_log"]["eid_scores"])
            for img in result["res_log"]["aligned_face_list"]:
                for face in img:
                    # face = np.moveaxis(face,0,2)
                    face=np.array(face,dtype="uint8")
                    face = np.transpose(face, (1, 2, 0))
                    face = cv2.cvtColor(face, cv2.COLOR_RGB2BGR)
                    # cv2.imwrite(res+"/{}.jpg".format(np.random.randint(1,1e5)),face)
                    cv2.imshow("Stream", face)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            count = count+1
            print("FPS: ",count/(time.time()-ts))


    ws.close()