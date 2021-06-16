import os, time
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from typing import List, Optional
from app.crud import fr_pgdb_crud as pgdb_crud
from app.db.schemas.fr_pgdb_schemas import (
    FRGroupDB,
    FRGroupCreate,
    FRUserDB,
    FRUserCreate,
    Message,
)

from app.db.utils.db_inits import get_db_sessions, DBSessions

# from app.core.analytics.job_scheduler import job_registration
from app.core.tasks.fr_redis_tasks import FRTasks

frtasks = FRTasks()
router = APIRouter()


@router.post(
    "/register_group", response_model=FRGroupDB, responses={404: {"model": Message}}
)  # , include_in_schema=False)
def register_group(*, db_sessions=Depends(get_db_sessions), group_in: FRGroupCreate):
    """
    Register FR Group.
    """
    group_response = pgdb_crud.register_group(
        pgdb_session=db_sessions.pgdbs, group_in=group_in,
    )

    if group_response["exists"]:
        return JSONResponse(
            status_code=404,
            content={
                "message": "FR Group with organiation :{}, team :{} already exists".format(
                    group_in.organization, group_in.team
                )
            },
        )
    else:
        return group_response["group_details"]


@router.get("/group_list", response_model=List[Optional[FRGroupDB]])
def get_frgroups(
    *, db_sessions=Depends(get_db_sessions),
):
    """
    List All FR Groups Details.
    """
    fr_groups = pgdb_crud.list_groups(pgdb_session=db_sessions.pgdbs)
    groups_response = []

    for group in fr_groups:
        groups_response.append(FRGroupDB(**jsonable_encoder(group)))
    return groups_response


@router.get("/group_details", response_model=FRGroupDB)
def get_group_details(*, db_sessions=Depends(get_db_sessions), groupUUID: str):
    """
    Retrieve FR Group Details.
    """
    group_details = pgdb_crud.get_group_UUID(
        pgdb_session=db_sessions.pgdbs, groupUUID=groupUUID
    )
    return FRGroupDB(**jsonable_encoder(group_details))


@router.post(
    "/register_user", response_model=FRUserDB, responses={404: {"model": Message}}
)
def register_fr_user(
    *,
    db_sessions=Depends(get_db_sessions),
    input_files: List[UploadFile] = File(...),
    eid: str = Form(...),
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
        ### delete user from table
        return JSONResponse(
            status_code=404, content={"message": "Error in user Face registration"}
        )


@router.post(
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


@router.get("/user_details", response_model=FRUserDB)
def get_user_details(*, db_sessions=Depends(get_db_sessions), eid: str):
    """
    Retrieve User Details using EID.
    """
    user_row = pgdb_crud.get_user_eid(pgdb_session=db_sessions.pgdbs, eid=eid)
    user_details = FRUserDB(
        **jsonable_encoder(user_row),
        groups=[
            FRGroupDB(**jsonable_encoder(user_group))
            for user_group in user_row.fr_group
        ],
    )
    return user_details


# @router.post("/create_inference_job", response_model=JobInDB, responses={404: {"model": Message}})
# def create_inference_job(
#     *,
#     pgdb: Session = Depends(get_pgdb),
#     mdb: MongoClient = Depends(get_mdb),
#     input_files: List[UploadFile] = File(...),
#     model_name: str = Form(...),
#     background_tasks: BackgroundTasks
#     ):
#     """
#     Create new job using analytics name.
#     """
#     model_details = pgdb_crud.get_model(pgdb_session=pgdb, model_name=model_name)
#     if model_details:
#         job_in = JobCreate(model_name = model_name)
#         job_details = pgdb_crud.create_job(pgdb_session=pgdb, job_in = job_in)
#         background_tasks.add_task( job_registration, pgdb=pgdb, mdb = mdb,
#             input_files = input_files, job_details = job_details)
#         return JobBaseInDB(**jsonable_encoder(job_details))
#     else:
#         return JSONResponse(status_code=404, content={"message": "No AI Model running with name :{}".format(model_name)})
