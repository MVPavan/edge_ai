import json, os
import time
import numpy as np
from loguru import logger
from FRModule.FRUtils.redis_utils import redis_conn
from FRModule.FRCore.fr_config import CoreConfig, FrQueues
from FRModule.FRUtils.strings import (
    FRTaskTypeEnum,
    FrResult,
    FrModesEnum,
    FrJob,
)
from FRModule.FaceDetection.fd_cam_process import FDCamProcess
from FRModule.FRUtils.VideoCapture import WebcamVideoStream

class FDCamWorker:
    def __init__(self,):
        self.stop = False
        self.fd_cam_process = FDCamProcess()
        self.start()

    def start(self,):
        while not self.stop:
            k, d = redis_conn.blpop(FrQueues.FRCInQ)
            tt = time.time()
            fr_job = FrJob(**json.loads(d.decode("utf-8")))
            cam = fr_job.fr_images
            if len(cam) == 1:
                cam = int(cam)
            video_capture = WebcamVideoStream(src=cam).start()
            grabbed,_ =  video_capture.read()
            while grabbed:
                if redis_conn.hexists(FrQueues.FRCInH,fr_job.task_id):
                    d = redis_conn.hget(FrQueues.FRCInH,fr_job.task_id)
                    assert(redis_conn.hdel(FrQueues.FRCInH,fr_job.task_id) == 1)
                    if d.decode("utf-8")=="stop":
                        video_capture.stop()
                        break
                grabbed,frame =  video_capture.read()
                if grabbed:
                    fr_job.fr_images = frame
                    tt1 = time.time()
                    fd_job_result = self.fd_cam_process.fdCamJob(fr_job = fr_job)
                    # redis_conn.publish(channel="FrChannel",message=fr_job_result.task_id)
                    te = time.time()
                    print("FD Up Time: {}, Processing Time: {}".format(tt1 - tt, te-tt1))
                    # logger.info("FD Total Time: {}".format(te - tt))
            redis_conn.hset(FrQueues.FRCOutH, fr_job.task_id, "stop")
            video_capture.stop()
            print("connection closed!")
                
            
# if __name__ == "__main__":
#     FDWorker()