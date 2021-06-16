import json
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.crud.fr_mdb_crud import get_task_log_by_oid
from app.db.models.fr_pgdb_models import FRGroups, FRUsers, FRTasks
from app.db.schemas.fr_pgdb_schemas import (
    FRGroupCreate,
    FRGroupDB,
    FRUserCreate,
    FRUserDB,
    FRTaskCreate,
    FRTaskLog,
    FRTaskLogOut,
    UserResponse,
)

# #############################################################################################################################################################
# ####################              UTILS                        ########################################
# #############################################################################################################################################################


def get_UUID_from_str(uuid_str: str):
    return uuid.UUID(uuid_str)


# #############################################################################################################################################################
# ####################              FR Group CRUD                        ########################################
# #############################################################################################################################################################


def get_group_UUID(pgdb_session: Session, *, groupUUID: str) -> Optional[FRGroups]:
    return pgdb_session.query(FRGroups).filter(FRGroups.groupUUID == groupUUID).first()


def get_groups_org(
    pgdb_session: Session, *, organization: str
) -> List[Optional[FRGroups]]:
    return (
        pgdb_session.query(FRGroups)
        .filter(FRGroups.organization == organization.lower())
        .all()
    )


def get_group_orgteam(
    pgdb_session: Session, *, organization: str, team: str
) -> Optional[FRGroups]:
    return (
        pgdb_session.query(FRGroups)
        .filter(FRGroups.organization == organization.lower())
        .filter(FRGroups.team == team.lower())
        .first()
    )


def list_groups(pgdb_session: Session) -> List[Optional[FRGroups]]:
    return pgdb_session.query(FRGroups).all()


def register_group(pgdb_session: Session, *, group_in: FRGroupCreate):
    group_response = {"exists": False, "group_details": []}
    group_details = get_group_orgteam(
        pgdb_session=pgdb_session,
        organization=group_in.organization,
        team=group_in.team,
    )
    if group_details:
        group_response["exists"] = True
    else:
        group_row = FRGroups(
            organization=group_in.organization,
            team=group_in.team,
            groupUUID=uuid.uuid4().hex,
        )
        pgdb_session.add(group_row)
        pgdb_session.commit()
        pgdb_session.refresh(group_row)
        group_details = FRGroupDB(**jsonable_encoder(group_row))
        group_response["group_details"] = group_details
    return group_response


# #############################################################################################################################################################
# ####################              FR User CRUD                        ########################################
# #############################################################################################################################################################


def get_user_eid(pgdb_session: Session, *, eid: str) -> Optional[FRUsers]:
    return pgdb_session.query(FRUsers).filter(FRUsers.eid == eid.lower()).first()


def check_user(pgdb_session: Session, *, eid: str):
    user_response = UserResponse()
    user_row = get_user_eid(pgdb_session=pgdb_session, eid=eid)
    if user_row:
        user_response.exists = True
    return user_response

def check_group(pgdb_session, groupUUID, eid = "", verify=False):
    group_response = UserResponse()
    group_row = get_group_UUID(pgdb_session=pgdb_session, groupUUID=groupUUID)
    if group_row:
        group_response.exists = True
    return group_response

def check_user_group(pgdb_session: Session, *, user_in: FRUserCreate):
    user_response = check_user(pgdb_session=pgdb_session, eid=user_in.eid)
    group_response = check_group(
        pgdb_session=pgdb_session, 
        groupUUID=user_in.groupUUID,
        eid=
        )
    if group_response.exists:
        user_response.grouped = True
    return user_response

def register_user(pgdb_session: Session, *, user_in: FRUserCreate):
    user_response = UserResponse()
    user_row = get_user_eid(pgdb_session=pgdb_session, eid=user_in.eid)
    if user_row:
        user_response.exists = True
        return user_response

    user_row = FRUsers(eid=user_in.eid, name=user_in.name)
    group_row = get_group_UUID(pgdb_session=pgdb_session, groupUUID=user_in.groupUUID)
    if group_row:
        user_row.fr_group.append(group_row)
        user_response.grouped = True
    else:
        user_response.grouped = False
        return user_response

    pgdb_session.add(user_row)
    pgdb_session.commit()
    pgdb_session.refresh(user_row)
    user_details = FRUserDB(
        **jsonable_encoder(user_row),
        groups=[
            FRGroupDB(**jsonable_encoder(user_group))
            for user_group in user_row.fr_group
        ]
    )
    user_response.user_details = user_details
    return user_response


def assign_group(pgdb_session: Session, *, user_in: FRUserCreate):
    user_row = get_user_eid(pgdb_session=pgdb_session, eid=user_in.eid)
    user_response = UserResponse(exists=True)
    if not user_row:
        user_response.exists = False
        return user_response

    group_row = get_group_UUID(pgdb_session=pgdb_session, groupUUID=user_in.groupUUID)
    if group_row:
        for user_group in user_row.fr_group:
            if str(user_group.groupUUID) == user_in.groupUUID:
                user_response.grouped = True
                return user_response
        user_row.fr_group.append(group_row)
        user_response.grouped = True
    else:
        user_response.grouped = False
        return user_response

    pgdb_session.add(user_row)
    pgdb_session.commit()
    pgdb_session.refresh(user_row)
    user_details = FRUserDB(
        **jsonable_encoder(user_row),
        groups=[
            FRGroupDB(**jsonable_encoder(user_group))
            for user_group in user_row.fr_group
        ]
    )
    user_response.user_details = user_details
    return user_response


# #############################################################################################################################################################
# ####################              TASKS CRUD                        ########################################
# #############################################################################################################################################################


def get_fr_task_by_id(pgdb_session: Session, *, task_id: int) -> Optional[FRTasks]:
    return pgdb_session.query(FRTasks).filter(FRTasks.id == task_id).first()


def get_fr_task_by_mdb_oid(
    pgdb_session: Session, *, task_mdb_oid: int
) -> Optional[FRTasks]:
    return pgdb_session.query(FRTasks).filter(FRTasks.mdb_oid == task_mdb_oid).first()


def get_fr_tasks_by_status(
    pgdb_session: Session, *, task_status: str
) -> Optional[FRTasks]:
    return pgdb_session.query(FRTasks).filter(FRTasks.task_status == task_status).all()


def insert_fr_tasks(pgdb_session: Session, *, fr_task: FRTaskCreate) -> FRTasks:
    if fr_task.fr_user:
        fr_task_row = FRTasks(
            task_type=fr_task.task_type,
            task_status=fr_task.task_status,
            fr_user=fr_task.fr_user,
            fr_group=fr_task.fr_group,
        )
    elif fr_task.fr_group:
        fr_task_row = FRTasks(
            task_type=fr_task.task_type,
            task_status=fr_task.task_status,
            fr_group=fr_task.fr_group,
        )
    else:
        fr_task_row = FRTasks(
            task_type=fr_task.task_type, task_status=fr_task.task_status
        )

    pgdb_session.add(fr_task_row)
    pgdb_session.commit()
    pgdb_session.refresh(fr_task_row)
    return fr_task_row


def update_task_log(
    pgdb_session: Session, *, task_id: int, task_log: FRTaskLog
) -> FRTasks:
    fr_task_db = get_fr_task_by_id(pgdb_session=pgdb_session, task_id=task_id)
    # fr_task_dict = jsonable_encoder(fr_task_db)
    task_log_dict = jsonable_encoder(task_log)
    for key, val in task_log_dict.items():
        if val:
            setattr(fr_task_db, key, val)
    pgdb_session.add(fr_task_db)
    pgdb_session.commit()
    pgdb_session.refresh(fr_task_db)
    return fr_task_db


def get_task_log_by_id(
    pgdb_session: Session, mdb_conn, *, task_id: int
) -> Optional[FRTaskLogOut]:
    task_log = get_fr_task_by_id(pgdb_session=pgdb_session, task_id=task_id)
    fr_task_log = FRTaskLogOut(**jsonable_encoder(task_log))
    mdb_task_log = get_task_log_by_oid(conn=mdb_conn, oid=fr_task_log.mdb_oid)
    fr_task_log.task_log = mdb_task_log.task_log
    return fr_task_log


def delete_fr_task(pgdb_session: Session, *, task_id: int):
    if get_fr_task_by_id(pgdb_session=pgdb_session, task_id=task_id):
        pgdb_session.query(FRTasks).filter(FRTasks.id == task_id).first().delete()
        pgdb_session.commit()
    return True
