import numpy as np
from loguru import logger
import time, pickle, uuid, os
from pathlib import Path
from FRCommon.fr_config import CoreConfig, FrQueues
from FRCommon.FRUtils.redis_utils import redis_conn
from FRCommon.FRUtils.img_utils import decodeIMG
from FRCommon.FRUtils.strings import (
    FRStatusEnum,
    TaskStatusEnum,
    FRTaskTypeEnum,
    FrResult,
    FrModesEnum,
    FrJob,
)
from FEModule.fe_handle import FEHandle

class FEProcess:
    def __init__(self,):
        self.fe_handle = FEHandle()
    
    def fdResultLoader(self):
        with open(self.fe_job.fr_result, "rb") as f : 
            self.fe_result = pickle.load(f)
        # self.fe_result = FrResult(**self.fe_job.fr_result)
        if os.path.exists(self.fe_job.fr_result):
            os.remove(self.fe_job.fr_result)
        self.aligned_face_list = self.fe_result.res_log["aligned_face_list"]
        self.embedding_list = []

    def feJob(self,fe_job:FrJob):
        self.fe_job = fe_job
        # self.imgLoader()
        t1s = time.time()
        self.fdResultLoader()
        t1e = time.time()
        print("FD Result Load time: ", t1e-t1s)
        t2s = time.time()
        self.faceEmbed()
        t2e = time.time()
        print("FE Embed time: ", t2e-t2s)
        if self.fe_job.task_type == FRTaskTypeEnum.FACE_REGISTER:
            t3s = time.time()
            self.regEmbed()
            t3e = time.time()
            print("FE reg time: ", t3e-t3s)
        t4s = time.time()
        self.fe_result.res_log["embedding_list"] = self.embedding_list
        self.fe_job.fr_result = (
            Path(CoreConfig.FR_RESULT_DIR, uuid.uuid4().hex)
            .with_suffix(".pkl")
            .as_posix()
        )
        with open(self.fe_job.fr_result, "wb") as f:
            pickle.dump(self.fe_result, f)
        t4i = time.time()
        self.fe_job.fr_images=[]
        redis_conn.rpush(FrQueues.ESInQ,self.fe_job.toJSON())
        t4e = time.time()
        print("FE Push:{},{}".format(t4i - t4s, t4e - t4s))
        return self.fe_job

    def faceEmbed(self):
        t3s = time.time()
        for img_aligned_faces in self.aligned_face_list:
            aligned_face=np.array(img_aligned_faces)
            face_embedding = self.fe_handle.embedFace(aligned_face=aligned_face)\
                .astype("float32", order='C')
            self.embedding_list.append(face_embedding)
        t3e = time.time()
        print("embedding timing: ",t3e-t3s)
        if self.fe_job.fr_mode == FrModesEnum.authenticate:
            del self.fe_result.res_log["aligned_face_list"] #save this in MinIO for Log
        # del self.fe_result.res_log["aligned_face_list"]
        return

    def regEmbed(self):
        fe_result = FrResult()
        self.embedding_list = np.array(self.embedding_list)
        if len(self.embedding_list.shape)==3 and \
            self.embedding_list.shape[1] == 1:
            self.embedding_list = self.embedding_list.mean(axis=0)
            fe_result.res_log["face_count"] = self.embedding_list.shape[0]
            self.fe_job.fr_status = FRStatusEnum.FACE_REGISTERED
            fe_result.success = True
        else:
            self.fe_job.fr_status = FRStatusEnum.MULTIPLE_FACE_DETECTED
            fe_result.success = False
            self.embedding_list = []
        self.fe_job.fr_result = fe_result
        redis_conn.hset(FrQueues.FROutH, self.fe_job.task_id, self.fe_job.toJSON())