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
from FRModule.FaceDetection.fd_process import FDProcess

class FDWorker:
    def __init__(self,):
        self.stop = False
        self.fd_process = FDProcess()
        self.start()

    def start(self,):
        while not self.stop:
            k, d = redis_conn.blpop(FrQueues.FRInQ)
            tt = time.time()
            fr_job = FrJob(**json.loads(d.decode("utf-8")))
            tt1 = time.time()
            fd_job_result = self.fd_process.fdJob(fr_job = fr_job)
            # redis_conn.publish(channel="FrChannel",message=fr_job_result.task_id)
            te = time.time()
            print("FD Json Time: {}, Processing Time: {}".format(tt1 - tt, te-tt1))
            logger.info("FD Total Time: {}".format(te - tt))
            
            
# if __name__ == "__main__":
#     FDWorker()