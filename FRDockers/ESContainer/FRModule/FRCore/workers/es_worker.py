import json
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
from FRModule.FRFeatures.es_process import ESProcess

class ESWorker:
    def __init__(self,):
        self.stop = False
        self.fe_process = ESProcess()
        self.start()

    def start(self,):
        while not self.stop:
            k, d = redis_conn.blpop(FrQueues.ESInQ)
            tt = time.time()
            es_job = FrJob(**json.loads(d.decode("utf-8")))
            ti = time.time()
            print("Q Load time: ",ti-tt)
            self.fe_process.esJob(es_job = es_job)
            # redis_conn.publish(channel="FrChannel",message=fr_job_result.task_id)
            te = time.time()
            logger.info("ES Processing Time: {}\n".format(te - tt))

# if __name__ == "__main__":
#     ESWorker()