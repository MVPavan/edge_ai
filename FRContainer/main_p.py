import time
from loguru import logger
from FRModule.FRCore.fr_config import CoreConfig, WorkerConfig
from imutils.video.webcamvideostream import WebcamVideoStream
from run_fd_worker import startFD
from run_fe_worker import startFE
from run_es_worker import startES

from multiprocessing import get_context
from multiprocessing import Process
from multiprocessing import Pool
from os import getpid

# class FRContainer:
#     def __init__(self,):
#         self.stop = False
#         self.workers = {
#             "fd":{"count":WorkerConfig.FD_Workers,"pids":[]},
#             "fe":{"count":WorkerConfig.FE_Workers,"pids":[]},
#             "es":{"count":WorkerConfig.ES_Workers,"pids":[]}
#         }
#         self.pause = 10

#     def initWorkers(self, key, _name):
#         if key == "fd":
#             _Q = RedisWorkerQueues.FDQ
#         if key=="fe":
#             _Q = RedisWorkerQueues.FEQ
#         if key=="es":
#             _Q = RedisWorkerQueues.ESQ
    
#         # t = Thread(target=spawn_worker, name=_name, args=(_Q, _name))
#         # # ##t.daemon = True
#         # t.start()
#         p = Process(target = spawn_worker, args=(_Q, _name))
#         p.start()
#         print("Started Process {}".format(_name))
#         return p

#     def start(self,):
#         for key in self.workers:
#             for i in range(self.workers[key]["count"]):
#                 self.workers[key]["enqueues"].append(self.initQueues(key,"{}_{}".format(key,i)))
#                 self.workers[key]["threads"].append(self.initWorkers(key,"{}_{}".format(key,i)))
#         while not self.stop:
#             time.sleep(self.pause)
#             self.workers
#             pass


def double(i):
    print("I'm process", getpid())
    return i * 2

def foo(q):
    print("I'm process", getpid())
    # q.put('hello')
    time.sleep(250)
    print("sleep Done  for:",getpid() )

if __name__ == '__main__':
    ctx = get_context('spawn')
    q = ctx.Queue()
    p1 = ctx.Process(target=foo, args=(q,))
    p1.start()
    p2 = ctx.Process(target=foo, args=(q,))
    p2.start()
    p3 = ctx.Process(target=foo, args=(q,))
    p3.start()
    p3.join()