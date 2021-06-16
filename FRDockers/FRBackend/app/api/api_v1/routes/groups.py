import os, time
from fastapi import APIRouter, Depends, File
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from app.crud import fr_pgdb_crud as pgdb_crud
from app.db.schemas.fr_pgdb_schemas import (
    FRGroupDB,
    FRGroupCreate,
    Message,
)
from typing import List, Optional
from app.db.utils.db_inits import get_db_sessions, DBSessions

group_router = APIRouter()

@group_router.post(
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

@group_router.get("/group_list", response_model=List[Optional[FRGroupDB]])
def group_list(
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


@group_router.get("/group_details", response_model=FRGroupDB)
def group_details(*, db_sessions=Depends(get_db_sessions), groupUUID: str):
    """
    Retrieve FR Group Details.
    """
    group_details = pgdb_crud.get_group_UUID(
        pgdb_session=db_sessions.pgdbs, groupUUID=groupUUID
    )
    return FRGroupDB(**jsonable_encoder(group_details))
