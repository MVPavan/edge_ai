import json
import time
import numpy as np
from loguru import logger
from rq import Queue as RJobQ
from rq import Worker, Connection
from FRModule.FRUtils.redis_utils import redis_conn
from FRModule.FRCore.fr_config import CoreConfig, FrQueues, RedisWorkerQueues, WorkerConfig
from threading import Thread
from multiprocessing import Process
from imutils.video.webcamvideostream import WebcamVideoStream
from run_fd_worker import startFD
from run_fe_worker import startFE
from run_es_worker import startES

def spawn_worker(_Q, _name):
    with Connection(redis_conn):
        worker = Worker(map(RJobQ, _Q), name=_name)
        print("started worker: ", _name)
        worker.work()
        print("Finished worker: ", _name)

class FRContainer:
    def __init__(self,):
        self.stop = False
        self.fdq = RJobQ(RedisWorkerQueues.FDQ, connection=redis_conn)
        self.feq = RJobQ(RedisWorkerQueues.FEQ, connection=redis_conn)
        self.esq = RJobQ(RedisWorkerQueues.ESQ, connection=redis_conn)
        self.workers = {
            "fd":{"count":WorkerConfig.FD_Workers,"enqueues":[],"threads":[]},
            "fe":{"count":WorkerConfig.FE_Workers,"enqueues":[],"threads":[]},
            "es":{"count":WorkerConfig.ES_Workers,"enqueues":[],"threads":[]}
        }
        self.pause = 10

    def initQueues(self, key, job_id):
        if key=="fd":
            job = self.fdq.enqueue(startFD, job_id=job_id)
        if key=="fe":
            job = self.feq.enqueue(startFE, job_id=job_id)
        if key=="es":
            job = self.esq.enqueue(startES, job_id=job_id)
        print("Finished Enqueuing {}".format(job_id))
        return job

    def initWorkers(self, key, _name):
        if key == "fd":
            _Q = RedisWorkerQueues.FDQ
        if key=="fe":
            _Q = RedisWorkerQueues.FEQ
        if key=="es":
            _Q = RedisWorkerQueues.ESQ
    
        # t = Thread(target=spawn_worker, name=_name, args=(_Q, _name))
        # # ##t.daemon = True
        # t.start()
        p = Process(target = spawn_worker, args=(_Q, _name))
        p.start()
        print("Started Process {}".format(_name))
        return p

    def start(self,):
        for key in self.workers:
            for i in range(self.workers[key]["count"]):
                self.workers[key]["enqueues"].append(self.initQueues(key,"{}_{}".format(key,i)))
                self.workers[key]["threads"].append(self.initWorkers(key,"{}_{}".format(key,i)))
        while not self.stop:
            time.sleep(self.pause)
            self.workers
            pass

