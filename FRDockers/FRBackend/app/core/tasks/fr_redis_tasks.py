import json, time, uuid
from pathlib import Path
from profilehooks import profile
from fastapi.encoders import jsonable_encoder
from app.db.utils.strings import (
    FRStatusEnum,
    TaskStatusEnum,
    FRTaskTypeEnum,
    FrResult,
    FrModesEnum,
    FrJob,
    DBSessions,
    SocketCamJob,
    SocketStreamJob
)
from app.db.utils import fr_utils, fastapi_utils
from app.db.utils.VideoCapture import WebcamVideoStream
from app.core.config import FRQueues, FrBuckets 
from app.db.utils.redis_utils import redis_conn as rc
from loguru import logger
from app.db.schemas.fr_pgdb_schemas import (
    FRGroupDB,
    FRGroupCreate,
    FRUserDB,
    FRUserCreate,
    FRTaskCreate,
    FRTaskLog,
    FRTaskLogOut,
    Message,
    Optional
)
from app.crud import fr_pgdb_crud as pgdbc
from app.crud import fr_mdb_crud as mdbc

class FRTaskDB:
    def __init__(self,):
        self.db_sessions:Optional[DBSessions]

    def frTaskCreate(self, fr_task):
        return pgdbc.insert_fr_tasks(
            pgdb_session=self.db_sessions.pgdbs, fr_task=fr_task
        )

    def frTaskUpdate(self, task_id, fr_task_log):
        return pgdbc.update_task_log(
            pgdb_session=self.db_sessions.pgdbs,
            task_id=task_id,
            task_log=fr_task_log,
        )

    def frTaskDelete(self, task_id):
        return pgdbc.delete_fr_task(
            pgdb_session=self.db_sessions.pgdbs, task_id=task_id
        )

    def frMDBLogInsert(self, task_log):
        return mdbc.insert_task_log(
            conn=self.db_sessions.mdbs, task_log=task_log
        )
    
    def frIO(self,fr_job):
        t1=time.time()
        fr_job_Q_json = fr_job.toJSON()
        # rc.rpush(FRQueues.FRInQ, json.dumps(fr_task_Q))
        rc.rpush(FRQueues.FRInQ, fr_job_Q_json)
        t2=time.time()
        print("Push Time: ",t2-t1)
        while True:
            if rc.hexists(FRQueues.FROutH,fr_job.task_id):
                break
            time.sleep(0.001)
        # for message in self.db_sessions.rpubsub.listen():
        #     if int(message["data"]) == fr_job.task_id:
        #         assert(rc.hexists(FRQueues.FROutH,fr_job.task_id))
        #         break
        d = rc.hget(FRQueues.FROutH,fr_job.task_id)
        assert(rc.hdel(FRQueues.FROutH,fr_job.task_id) == 1)
        # _, d = rc.blpop(FRQueues.FROutQ)
        return json.loads(d.decode("utf-8"))

    def registerUser(self,user_in):
        return pgdbc.register_user(
            pgdb_session=self.db_sessions.pgdbs, user_in=user_in,
        )

class FRTasks:
    def __init__(self):
        self.task_db = FRTaskDB()
        self.task_id = None
        self.fr_images = []

    # self._fr_images.append({"img_id": im_file.filename, "image": tempImage})
    def imageRead(self, fr_image_files):
        self.fname, self.fr_images = [], []
        self.task_id = uuid.uuid4().hex
        t1=time.time()
        for i,im_file in enumerate(fr_image_files):
            # fname = Path("/home/pavanmv/Pavan/HW/FR/FR_MS/data/{}_{}".format(self.task_id,i))
            # fastapi_utils.save_upload_file(im_file,fname)
            # self.fr_images.append(fname.as_posix())
            tempImage = im_file.file.read()
            self.fr_images.append(fr_utils.encodeIMG(tempImage))
        t2=time.time()
        print("Img Encode: ",t2-t1)
        # print("wow")

    def taskInit(
        self,
        task_type:FRTaskTypeEnum,
        fr_group=None,
        fr_user=None, 
        evaluate=False):  
        fr_job = FrJob()
        fr_job.fr_images = self.fr_images
        fr_job.task_type = task_type
        fr_job.fr_group,fr_job.fr_user = fr_group,fr_user
        # fr_task_db = self.task_db.frTaskCreate(
        #     FRTaskCreate(**fr_job.toDict(), task_status=TaskStatusEnum.inqueue)
        # )
        # fr_job.task_id = fr_task_db.id
        fr_job.task_id = self.task_id
        if evaluate:
            fr_job.fr_mode = FrModesEnum.evaluate
        return fr_job
    
    def taskUpdate(self, fr_job_result:FrJob, user_in, evaluate=True):
        _response = FrResult(**fr_job_result.fr_result)
        if evaluate:
            # self.task_db.frTaskDelete(fr_job_result.task_id)
            return _response
        fr_task_log = FRTaskLog(**fr_job_result.toDict())
        if _response.success:
            mdb_log = self.task_db.frMDBLogInsert(task_log=json.dumps(_response.res_log))
            fr_task_log.mdb_oid = mdb_log.oid
            fr_task_log.task_status = TaskStatusEnum.passed
            if fr_task_log.task_type == FRTaskTypeEnum.FACE_REGISTER:
                user_response = self.task_db.registerUser(user_in)
                _response.res_log = user_response
        else:
            fr_task_log.task_status = TaskStatusEnum.failed
            if fr_task_log.task_type == FRTaskTypeEnum.FACE_REGISTER:
                fr_task_log.fr_user = None
                fr_task_log.fr_group = None
        # fr_task_db = self.task_db.frTaskUpdate(fr_job_result.task_id , fr_task_log )
        fr_task_db = self.task_db.frTaskCreate(fr_task_log)
        return _response
        
    # @profile(immediate=True)
    def frRegister(self, db_sessions, user_in: FRUserCreate, fr_image_files, evaluate=False):
        self.task_db.db_sessions = db_sessions
        self.imageRead(fr_image_files)
        fr_job = self.taskInit(
            task_type=FRTaskTypeEnum.FACE_REGISTER,
            fr_group=user_in.groupUUID,
            fr_user=user_in.eid,
            evaluate=evaluate
        )
        fr_job_result=FrJob(**self.task_db.frIO(fr_job))
        return self.taskUpdate(fr_job_result=fr_job_result,user_in = user_in,evaluate=evaluate)

    def frDetect(self, db_sessions, fr_image_files, evaluate=True):
        self.task_db.db_sessions = db_sessions
        self.imageRead(fr_image_files)
        fr_job = self.taskInit(task_type=FRTaskTypeEnum.FACE_DETECT,evaluate=evaluate)
        fr_job_result=FrJob(**self.task_db.frIO(fr_job))
        return self.taskUpdate(fr_job_result, evaluate)
         
    def frIdentify(self, db_sessions, fr_image_files, groupUUID=None, evaluate=False):
        self.task_db.db_sessions = db_sessions
        self.imageRead(fr_image_files)
        fr_job = self.taskInit(
            task_type=FRTaskTypeEnum.FACE_IDENTIFY,
            fr_group=groupUUID,
            evaluate=evaluate
        )
        fr_job_result=FrJob(**self.task_db.frIO(fr_job))
        return self.taskUpdate(fr_job_result,evaluate)

    def frVerify(self, db_sessions, fr_image_files, eid, groupUUID=None, evaluate=False):
        self.task_db.db_sessions = db_sessions
        self.imageRead(fr_image_files)
        fr_job = self.taskInit(
            task_type=FRTaskTypeEnum.FACE_VERIFY,
            fr_user=eid,
            fr_group=groupUUID,
            evaluate=evaluate
        )
        fr_job_result=FrJob(**self.task_db.frIO(fr_job))
        return self.taskUpdate(fr_job_result,evaluate)

    def frCompare(self, db_sessions, fr_image_file_1, fr_image_file_2):
        '''
        Compare two images and give similarity score
        '''
        return FrResult()

    def frCam(self,soc_job:SocketCamJob):
        self.fr_images = soc_job.cam_link
        self.task_id = uuid.uuid4().hex
        fr_cam_job = self.taskInit(
            task_type=FRTaskTypeEnum.FACE_IDENTIFY,
            fr_group=soc_job.groupUUID,
            evaluate=True
        )
        fr_cam_job_Q_json = fr_cam_job.toJSON()
        # rc.rpush(FRQueues.FRInQ, json.dumps(fr_task_Q))
        rc.rpush(FRQueues.FRCInQ, fr_cam_job_Q_json)
        return self.task_id
    
    


# ######## extract image from redis and convert to cv2 format
# def test():
#     _,d = rc.blpop(FRQueues.FRInQ)
#     q = json.loads(d.decode("utf-8"))
#     fr_images=[fr_utils.decodeIMG(fr_img["image"],name=fr_img["img_id"],dtype=fr_utils.IMAGE_DTYPE) \
#         for fr_img in q["fr_images"]]
#     fr_ids=[fr_img["img_id"] for fr_img in q["fr_images"]]
#     print(fr_ids)

# ## Just upload in minio and send object name in redis
# @profile(immediate=True)
# def frUpload(fr_image_file,mio):
#     fputs = mio.fput_fastapi_objects("logs", fr_image_file)
#     k="img"
#     d = {"img_id": k, "image": fr_image_file[0].filename}
#     rc.rpush(FRQueues.FRInQ, json.dumps(d))
#     # test_(mio)
#     pass

# def test_(mio):
#     _,d = rc.blpop(FRQueues.FRInQ)
#     q = json.loads(d.decode("utf-8"))
#     g=mio.get_multi_object("logs")
#     # print(g)
