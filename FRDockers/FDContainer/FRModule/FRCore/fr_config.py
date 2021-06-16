import os
import numpy as np
from loguru import logger
# from line_profiler import LineProfiler
# import atexit

# tprofile = LineProfiler()
# atexit.register(tprofile.print_stats)

class RedisDB:
    REDIS_SERVER = os.getenv("REDIS_SERVER", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_QUEUES = os.getenv("REDIS_QUEUES", ["low", "default", "high"])
    REDIS_DB = os.getenv("REDIS_DB", 0)

class CoreConfig:
    GPU_DEVICE = int(os.getenv("GPU_DEVICE", 0))  # GPU ID, -1 for CPU
    IMAGE_DTYPE = np.uint8  # Image decode type converter form redis queue recieve
    FR_RESULT_DIR = "Data/"
    
class FDConfig:
    FD_MTCNN_CAFFE_WEIGHTS = "FRModule/FRWeights/mtcnn_caffe_model"
    MTCNN_DET_MODE = 0  # mtcnn option, 1 means using R+O, 0 means detect from begining
    MTCNN_NETWORK_THRESHOLDS = [0.6, 0.7, 0.8]
    FD_MIN_SIZE = 100  # MIN PIXELS FOR FACE
    FD_CONFIDENCE_THRESHOLD = 0.7
    FR_IMAGE_SIZE = (112, 112)

class FrQueues:
    FRInQ = os.getenv("FRInQ", "FRInQ")
    FEInQ = os.getenv("FEInQ", "FEInQ")
    FROutH = os.getenv("FROutH", "FROutH")
