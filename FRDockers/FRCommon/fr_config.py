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
    GPU_DEVICE = int(os.getenv("GPU_DEVICE", -1))  # GPU ID, -1 for CPU
    IMAGE_DTYPE = np.uint8  # Image decode type converter form redis queue recieve
    FR_FEATURE_DIR = "ESModule/ESFeatures/DB"
    FR_RESULT_DIR = "Data"
    grp_embeds = "_embeds"
    grp_ids = "_ids"
    groups = "groups"

class FDConfig:
    FD_MTCNN_CAFFE_WEIGHTS = "FDModule/FDWeights/mtcnn_caffe_model"
    MTCNN_DET_MODE = 0  # mtcnn option, 1 means using R+O, 0 means detect from begining
    MTCNN_NETWORK_THRESHOLDS = [0.6, 0.7, 0.8]
    FD_MIN_SIZE = 100  # MIN PIXELS FOR FACE
    FD_CONFIDENCE_THRESHOLD = 0.7
    FR_IMAGE_SIZE = (112, 112)

class FEConfig:
    FD_CONFIDENCE_THRESHOLD = 0.7
    FR_IMAGE_SIZE = (112, 112)
    FR_AFIF_MXNET_WEIGHTS = "FEModule/FEWeights/IFModel/model-r100-ii/"
    FR_FLIP = 0  # 1 - calculates average embedding of original and right flipped face image
    FR_DISTANCE_THRESHOLD = 1.24
    FE_DISTANCE_THRESHOLD = 0.9
    FE_SIMILARITY_THRESHOLD = 0.52


class FrQueues:
    FRInQ = os.getenv("FRInQ", "FRInQ")
    FROutH = os.getenv("FROutH", "FROutH")
    FROutQ = os.getenv("FROutQ", "FROutQ")
    FEInQ = os.getenv("FEInQ", "FEInQ")
    FEOutQ = os.getenv("FEOutQ", "FEOutQ")
    FDOutQ = os.getenv("FDOutQ", "FDOutQ")
    ESInQ = os.getenv("ESInQ", "ESInQ")
    ESOutQ = os.getenv("ESOutQ", "ESOutQ")
    