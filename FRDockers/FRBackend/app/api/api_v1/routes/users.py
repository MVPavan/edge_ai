import os, time
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
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
from app.core.tasks.fr_redis_tasks import FRTasks

frtasks = FRTasks()
user_router = APIRouter()

def _eid(eid:str):
    return eid.lower()

@user_router.post(
    "/register_user", response_model=FRUserDB, responses={404: {"model": Message}}
)
def register_user(
    *,
    db_sessions=Depends(get_db_sessions),
    input_files: List[UploadFile] = File(...),
    eid: str = Form(...),
    # eid: str = Depends(_eid),
    name: str = Form(...),
    groupUUID: str = Form(...),
    background_tasks: BackgroundTasks,
):
    """
    Register New User in FR Server.
    """
    eid = eid.lower()
    user_in = FRUserCreate(eid=eid, name=name, groupUUID=groupUUID)
    user_response = pgdb_crud.check_user_group(
        pgdb_session=db_sessions.pgdbs, user_in=user_in,
    )
    tt = time.time()
    if user_response.exists:
        return JSONResponse(
            status_code=404,
            content={
                "message": "FR user with eid :{} already exists".format(user_in.eid)
            },
        )
    elif not user_response.grouped:
        return JSONResponse(
            status_code=404,
            content={"message": "User could not be assosciated with Group"},
        )
    _response = frtasks.frRegister(
        db_sessions, user_in=user_in, fr_image_files=input_files
    )
    if _response.success:
        print("face_register time : ", time.time() - tt)
        return _response.res_log.user_details
    else:
        return JSONResponse(
            status_code=404, content={"message": "Error in user Face registration"}
        )

@user_router.post(
    "/assign_group", response_model=FRUserDB, responses={404: {"model": Message}}
)
def assign_group(
    *,
    db_sessions=Depends(get_db_sessions),
    eid: str = Form(...),
    groupUUID: str = Form(...),
):
    """
    Assign a Group to Existing User.
    """
    user_in = FRUserCreate(eid=eid, groupUUID=groupUUID)
    user_response = pgdb_crud.assign_group(
        pgdb_session=db_sessions.pgdbs, user_in=user_in,
    )
    if not user_response.exists:
        return JSONResponse(
            status_code=404,
            content={
                "message": "FR user with eid :{} does not exists".format(user_in.eid)
            },
        )
    elif not user_response.grouped:
        return JSONResponse(
            status_code=404,
            content={"message": "Group with UUID: {} does not exist".format(groupUUID)},
        )
    elif not user_response.user_details:
        return JSONResponse(
            status_code=404,
            content={"message": "User is already enrolled in given group"},
        )
    else:
        return user_response.user_details

@user_router.get("/user_details", response_model=FRUserDB)
def user_details(*, db_sessions=Depends(get_db_sessions), eid: str):
    """
    Retrieve User Details using EID.
    """
    user_row = pgdb_crud.get_user_eid(pgdb_session=db_sessions.pgdbs, eid=eid)
    if user_row:
        user_details = FRUserDB(
            **jsonable_encoder(user_row),
            groups=[
                FRGroupDB(**jsonable_encoder(user_group))
                for user_group in user_row.fr_group
            ],
        )
        return user_details
    else:
        return JSONResponse(
            status_code=404,
            content={
                "message": "FR user with eid :{} does not exists".format(eid)
            },
        )