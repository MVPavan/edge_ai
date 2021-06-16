import os, time, json
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    Cookie,
    Header,
    WebSocket,
    status,
)
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from typing import List, Optional
from app.crud import fr_pgdb_crud as pgdb_crud
from app.db.schemas.fr_pgdb_schemas import (
    FRGroupDB,
    FRUserDB,
    FRUserCreate,
    Message,
)

from app.db.utils.db_inits import get_db_sessions, DBSessions
from app.core.tasks.fr_redis_tasks import (
    rc,
    FRQueues,
    FRTasks,
    SocketCamJob,
    SocketStreamJob,
    WebcamVideoStream,
    fr_utils
)

frtasks = FRTasks()
fr_ops_router = APIRouter()
# def frDetect(self, db_sessions, fr_image_files, evaluate=True):
# def frIdentify(self, db_sessions, fr_image_files, groupUUID=None, evaluate=False):
# def frVerify(self, db_sessions, fr_image_files, eid, groupUUID=None, evaluate=False):

# response_model=FRUserDB,
@fr_ops_router.post("/detect", responses={404: {"model": Message}})
def detect(
    *, db_sessions=Depends(get_db_sessions), input_files: List[UploadFile] = File(...),
):
    """
    Detect Face.
    """
    ts = time.time()
    _response = frtasks.frDetect(db_sessions, fr_image_files=input_files)
    if _response.success:
        print("face_detect time : ", time.time() - ts)
        return _response.res_log
    else:
        return JSONResponse(
            status_code=404, content={"message": "Error in Face Detection"}
        )


# response_model=FRUserDB,
@fr_ops_router.post("/identify", responses={404: {"model": Message}})
def identify(
    *,
    db_sessions=Depends(get_db_sessions),
    input_files: List[UploadFile] = File(...),
    groupUUID: str = Form(...),
):
    """
    Identify Face in a group.
    """
    group_response = pgdb_crud.check_group(
        pgdb_session=db_sessions.pgdbs, groupUUID=groupUUID,
    )
    if not group_response.exists:
        return JSONResponse(
            status_code=404,
            content={"message": "Group :{} does not exists".format(groupUUID)},
        )
    ts = time.time()
    _response = frtasks.frIdentify(
        db_sessions, fr_image_files=input_files, groupUUID=groupUUID
    )
    if _response.success:
        print("Face Identify time : ", time.time() - ts)
        return _response.res_log
    else:
        return JSONResponse(
            status_code=404, content={"message": "Error in Face Identify"}
        )


@fr_ops_router.post("/verify", responses={404: {"model": Message}})
def verify(
    *,
    db_sessions=Depends(get_db_sessions),
    input_files: List[UploadFile] = File(...),
    groupUUID: str = Form(...),
    eid: str = Form(...),
):
    """
    Verify Face with the one stored in Group,EID.
    """
    eid = eid.lower()
    user_in = FRUserCreate(eid=eid, name="*", groupUUID=groupUUID)
    user_response = pgdb_crud.check_user_group(
        pgdb_session=db_sessions.pgdbs, user_in=user_in,
    )
    if not user_response.exists:
        return JSONResponse(
            status_code=404,
            content={
                "message": "User with eid :{} does not exists".format(user_in.eid)
            },
        )
    elif not user_response.grouped:
        return JSONResponse(
            status_code=404,
            content={"message": "Group :{} does not exists".format(groupUUID)},
        )
    ts = time.time()
    _response = frtasks.frVerify(
        db_sessions, fr_image_files=input_files, groupUUID=groupUUID, eid=eid
    )
    if _response.success:
        print("Face Verify time : ", time.time() - ts)
        return _response.res_log
    else:
        return JSONResponse(
            status_code=404, content={"message": "Error in Face Identify"}
        )


@fr_ops_router.post(
    "/compare", responses={404: {"model": Message}}, include_in_schema=False
)
def compare(
    *,
    db_sessions=Depends(get_db_sessions),
    input_file_1: UploadFile = File(...),
    input_file_2: UploadFile = File(...),
):
    """
    Verify Face with the one stored in Group,EID.
    """
    ts = time.time()
    _response = frtasks.frCompare(
        db_sessions=db_sessions,
        fr_image_file_1=input_file_1,
        fr_image_file_2=input_file_2,
    )
    if _response.success:
        print("face_detect time : ", time.time() - ts)
        return _response.res_log
    else:
        return JSONResponse(
            status_code=404, content={"message": "Error in Face Identify"}
        )


async def get_cookie_or_client(
    websocket: WebSocket, session: str = Cookie(None), x_client: str = Header(None)
):
    if session is None and x_client is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or x_client


@fr_ops_router.websocket_route("/ws/infer")
async def websocket_infer(
    websocket: WebSocket, cookie_or_client: str = Depends(get_cookie_or_client),
):
    task_id = None
    try:
        await websocket.accept()
        await websocket.send_json(SocketCamJob().toDict())
        data = await websocket.receive_json()
        soc_job = SocketCamJob(**data)
        if soc_job.mask_detection and soc_job.groupUUID:
            task_id = frtasks.frCam(soc_job=soc_job)
            while True:
                time.sleep(0.005)
                if rc.hexists(FRQueues.FRCOutH, task_id):
                    d = rc.hget(FRQueues.FRCOutH, task_id)
                    assert rc.hdel(FRQueues.FRCOutH, task_id) == 1
                    d = d.decode("utf-8")
                    if d != "stop":
                        cam_job = json.loads(d)
                        await websocket.send_json(cam_job["fr_result"])
                    else:
                        await websocket.send_text("stop")
                        await websocket.close()
                        print("Closed Websocket session!!")
                        break
        else:
            await websocket.close()
    except Exception as e:
        print("Got exception {}".format(e))
        if task_id:
            rc.hset(FRQueues.FRCInH, task_id, "stop")
        pass


@fr_ops_router.websocket_route("/ws/stream")
async def websocket_stream(
    websocket: WebSocket, cookie_or_client: str = Depends(get_cookie_or_client),
):
    video_capture = None
    try:
        await websocket.accept()
        await websocket.send_json(SocketStreamJob().toDict())
        data = await websocket.receive_json()
        stream_job = SocketStreamJob(**data)
        if stream_job.cam_link:
            video_capture = WebcamVideoStream(src=stream_job.cam_link).start()
            grabbed,_ =  video_capture.read()
            while grabbed:
                grabbed,frame =  video_capture.read()
                frame = fr_utils.encodeCVIMG(frame)
                await websocket.send_bytes(frame)
                # frame_dict = {
                #     "frame": fr_utils.encodeCVIMG(frame),
                #     "timestamp": time.time()
                # }
                # await websocket.send_json(frame_dict)

            # await websocket.send_text("stop")
        await websocket.close()
        print("Closed Websocket session!!")
    except Exception as e:
        print("Got exception {}".format(e))
        if video_capture:
            video_capture.stop()
        