import numpy as np
from loguru import logger
import time, pickle, os
from FRCommon.fr_config import CoreConfig, FEConfig, FrQueues
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
from ESModule.es_handle import ESHandle

'''
saving of new embedding can be optimized using workers
'''
class ESProcess:
    def __init__(self,):
        self.es_handle = ESHandle()

    def feResultLoader(self):
        with open(self.es_job.fr_result, "rb") as f : 
            self.es_result = pickle.load(f)
        if os.path.exists(self.es_job.fr_result):
            os.remove(self.es_job.fr_result)
        self.embedding_list = self.es_result.res_log["embedding_list"]
        self.eid_scores = []

    def esJob(self, es_job: FrJob):
        self.es_job = es_job
        t1s = time.time()
        self.feResultLoader()
        t1e = time.time()
        print("FE Result Load time: ", t1e-t1s)
        if self.es_job.task_type == FRTaskTypeEnum.FACE_IDENTIFY:
            t1s = time.time()        
            for embeddings in self.embedding_list:
                self.eid_scores.append(np.copy(self.embedSearch(embeddings)))
            t1e = time.time()
            print("Identity Search time: ", t1e-t1s)
            self.es_result.res_log["eid_scores"] = self.eid_scores
            del self.es_result.res_log["embedding_list"]
            self.es_job.fr_result = self.es_result
            if self.es_job.fr_mode == FrModesEnum.authenticate:
                redis_conn.hset(FrQueues.FROutH, self.es_job.task_id, self.es_job.toJSON())
            else:
                print("pushing to: ",self.es_job.task_id)
                redis_conn.hset(FrQueues.FRCOutH, self.es_job.task_id, self.es_job.toJSON())
                
            t1e1 = time.time()
            print("Identity Push time: ", t1e1-t1e)
            
        elif self.es_job.task_type == FRTaskTypeEnum.FACE_VERIFY:
            t1s = time.time()        
            for embeddings in self.embedding_list:
                self.eid_scores.append(np.copy(self.embedMatch(embeddings)))
            t1e = time.time()
            print("Verify Search time: ", t1e-t1s)
            self.es_result.res_log["eid_scores"] = self.eid_scores
            del self.es_result.res_log["embedding_list"]
            self.es_job.fr_result = self.es_result
            
            redis_conn.hset(FrQueues.FROutH, self.es_job.task_id, self.es_job.toJSON())
            t1e1 = time.time()
            print("Identity Push time: ", t1e1-t1e)
            
        elif self.es_job.task_type == FRTaskTypeEnum.FACE_REGISTER:
            t1s = time.time()
            self.es_handle.updateNewEmbed(
                face_embedding=self.embedding_list,
                groupUUID = self.es_job.fr_group,
                eid = self.es_job.fr_user
            )
            t1e = time.time()
            print("Register time: ", t1e-t1s)
            
        else:
            logger.info("Program in grave Danger!!")
        return

    def embedSearch(self, embeddings):
        D,I = self.es_handle.embedSearch(
            groupUUID = self.es_job.fr_group,
            queryVec = embeddings,
            neighbours = 1
        )
        eids = self.es_handle.getEIDS(
            groupUUID = self.es_job.fr_group,
            idx = I[:, 0]
            )# use FE_DISTANCE_THRESHOLD for L2
        eids[D[:,0] < FEConfig.FE_SIMILARITY_THRESHOLD] = "unknown"
        eid_similarity = np.stack((D[:,0].reshape(-1,1),eids),axis=1)
        return eid_similarity

    def embedMatch(self, embeddings):
        D,I = self.es_handle.embedMatch(
            queryVec = embeddings,
            groupUUID=self.es_job.fr_group,
            eid=self.es_job.fr_user
        )
        eid_similarity = D[:,0]
        return eid_similarity