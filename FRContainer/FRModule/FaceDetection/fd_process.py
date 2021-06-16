import numpy as np
from loguru import logger
from pathlib import Path
import time, pickle, uuid

import cv2
from FRModule.FRCore.fr_config import tprofile, CoreConfig, FrQueues
from FRModule.FRUtils.redis_utils import redis_conn
from FRModule.FRUtils.img_utils import decodeIMG, encodeIMG
from numpy import savez, load
from FRModule.FRUtils.strings import (
    FRStatusEnum,
    TaskStatusEnum,
    FRTaskTypeEnum,
    FrResult,
    FrModesEnum,
    FrJob,  # FEJob
)
from FRModule.FRCore.fr_handle import FDHandle

class FDProcess:
    def __init__(self,):
        self.fd_handle = FDHandle()

    def reset(self):
        self.bbox_list = []
        self.landmarks_list = []
        self.aligned_face_list = []

    def imgLoader(self):
        self.fr_image_list = [decodeIMG(fr_img) for fr_img in self.fd_job.fr_images]
        # self.fr_image_list = [cv2.imread(fr_img) for fr_img in self.fd_job.fr_images]
        self.fd_job.fr_images = []

    def fdJob(self, fr_job: FrJob):
        self.reset()
        self.fd_job = fr_job
        self.fd_job.fr_status = FRStatusEnum.FACE_NOT_DETECTED
        t2s = time.time()
        self.imgLoader()
        t2e = time.time()
        print("IMLoad: ", t2e-t2s)
        t3s = time.time()
        self.faceDetect(align=True)
        t3e = time.time()
        print("Detect: ", t3e-t3s)
        
        if self.fd_job.fr_result.success:
            if self.fd_job.task_type != FRTaskTypeEnum.FACE_DETECT:
                t4s = time.time()
                del self.fd_job.fr_result.res_log["landmark_list"]
                fe_input = (
                    Path(CoreConfig.FR_RESULT_DIR, uuid.uuid4().hex)
                    .with_suffix(".pkl")
                    .as_posix()
                )
                with open(fe_input, "wb") as f:
                    pickle.dump(self.fd_job.fr_result, f)
                self.fd_job.fr_result = fe_input
                t4i = time.time()
                redis_conn.rpush(FrQueues.FEInQ, self.fd_job.toJSON())
                t4e = time.time()
                print("FD Push:{},{}".format(t4i - t4s, t4e - t4s))    
                # print(self.aligned_face_list)
                return self.fd_job
            self.fd_job.fr_status = FRStatusEnum.FACE_DETECTED
            del self.fd_job.fr_result.res_log["aligned_face_list"]
        redis_conn.hset(FrQueues.FROutH, self.fd_job.task_id, self.fd_job.toJSON())
        t5 = time.time()
        print("FD Push:{}".format(t5-t3e))
        return self.fd_job

    def faceDetect(self, align=False):
        face_count = 0
        for img in self.fr_image_list:
            t1s = time.time()
            (bbox_list, landmarks_list) = self.fd_handle.detectFace(img=img)
            t1e = time.time()
            print("FD Detect:{}".format(t1e - t1s))
            if len(bbox_list):
                t2s = time.time()
                (aligned_faces, bbox_list_conf) = self.fd_handle.alignFace(
                    img=img, bbox_list=bbox_list, landmarks_list=landmarks_list
                )
                t2e = time.time()
                print("Align:{}".format(t2e - t2s))
                self.bbox_list.append(bbox_list_conf)
                self.aligned_face_list.append(aligned_faces)
                self.landmarks_list.append(landmarks_list)
                face_count += len(aligned_faces)
        print("detected Face Count: {}".format(face_count))
        self.detectResult()
        
    def detectResult(self):
        fr_result = FrResult()
        if any(self.bbox_list):
            fr_result.success = True
            fr_result.res_log = {
                "bbox_list": self.bbox_list,
                "landmark_list": self.landmarks_list,
                "aligned_face_list": self.aligned_face_list,
            }
            # fr_result.res_log = encodeIMG(k)
        self.fd_job.fr_result = fr_result

    # def embedFace(self):
    # fe_job = FEJob(**self.fd_job.toDict())
    # fe_job.aligned_face_list = self.aligned_face_list
    # fe_job.bbox_list = self.bbox_list
    # return fe_job.toJSON()
