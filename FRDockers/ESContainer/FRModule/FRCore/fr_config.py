import os
import numpy as np
from loguru import logger

class RedisDB:
    REDIS_SERVER = os.getenv("REDIS_SERVER", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_QUEUES = os.getenv("REDIS_QUEUES", ["low", "default", "high"])
    REDIS_DB = os.getenv("REDIS_DB", 0)

class CoreConfig:
    GPU_DEVICE = int(os.getenv("GPU_DEVICE", 0))  # GPU ID, -1 for CPU
    IMAGE_DTYPE = np.uint8  # Image decode type converter form redis queue recieve
    FR_FEATURE_DIR = "FRModule/FRFeatures/DB"
    FR_RESULT_DIR = "Data"
    grp_embeds = "_embeds"
    grp_ids = "_ids"
    groups = "groups"
    

class FEConfig:
    FR_IMAGE_SIZE = (112, 112)
    FR_AFIF_MXNET_WEIGHTS = "FRModule/FRWeights/IFModel/model-r100-ii/"
    FR_FLIP = 0  # 1 - calculates average embedding of original and right flipped face image
    FR_DISTANCE_THRESHOLD = 1.24
    FE_DISTANCE_THRESHOLD = 0.9
    FE_SIMILARITY_THRESHOLD = 0.52


class FrQueues:
    FRInQ = os.getenv("FRInQ", "FRInQ")
    FROutQ = os.getenv("FROutQ", "FROutQ")
    FEInQ = os.getenv("FEInQ", "FEInQ")
    FEOutQ = os.getenv("FEOutQ", "FEOutQ")
    FDOutQ = os.getenv("FDOutQ", "FDOutQ")
    ESInQ = os.getenv("ESInQ", "ESInQ")
    ESOutQ = os.getenv("ESOutQ", "ESOutQ")
    FROutH = os.getenv("FROutH", "FROutH")
