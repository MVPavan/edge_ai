import json, os
import time
import numpy as np
from loguru import logger
from FRCommon.FRUtils.redis_utils import redis_conn
from FRCommon.fr_config import CoreConfig, FrQueues
from FRCommon.FRUtils.strings import (
    FRTaskTypeEnum,
    FrResult,
    FrModesEnum,
    FrJob,
)
from FEModule.FaceEmbedding.fe_process import FEProcess

class FEWorker:
    def __init__(self,):
        self.stop = False
        self.fe_process = FEProcess()
        self.start()

    def start(self,):
        while not self.stop:
            k, d = redis_conn.blpop(FrQueues.FEInQ)
            tt = time.time()
            fe_job = FrJob(**json.loads(d.decode("utf-8")))
            ti = time.time()
            fe_job_result = self.fe_process.feJob(fe_job)
            # redis_conn.publish(channel="FrChannel",message=fr_job_result.task_id)
            te = time.time()
            print("FE Json Time: {}, Processing Time: {}".format(ti-tt, te-ti))
            logger.info("FE Total Time: {}".format(te - tt))
            

# if __name__ == "__main__":
#     FEWorker()