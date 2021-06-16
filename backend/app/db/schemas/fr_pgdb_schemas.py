from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, ValidationError, Json, UUID4
from app.db.utils.strings import FRStatusEnum, FRTaskTypeEnum, TaskStatusEnum

##########################################################################################################################
##########################       GROUP SCHEMAS       #######################################################################
##########################################################################################################################
class FRGroupBase(BaseModel):
    organization: str
    team: str


class FRGroupCreate(FRGroupBase):
    pass


class FRGroupDB(FRGroupBase):
    groupUUID: str


##########################################################################################################################
##########################       USER SCHEMAS       #######################################################################
##########################################################################################################################


class FRUserBase(BaseModel):
    name: Optional[str]
    eid: str

class FRUserCreate(FRUserBase):
    groupUUID: str


class FRUserDB(FRUserBase):
    groups: List[Optional[FRGroupDB]]


##########################################################################################################################
##########################       TASK SCHEMAS       #######################################################################
##########################################################################################################################


class FRTaskBase(BaseModel):
    task_type: Optional[FRTaskTypeEnum]
    task_status: TaskStatusEnum = TaskStatusEnum.inqueue

class FRTaskCreate(FRTaskBase):
    fr_group: Optional[str]
    fr_user: Optional[str]

class FRTaskInDB(FRTaskCreate):
    id: int
    # task_log : Optional[Json]
    class config:
        orm_mode = True
        validate_assignment = True

class FRTaskLog(FRTaskCreate):
    mdb_oid: Optional[str]
    fr_status: Optional[FRStatusEnum]

class FRTaskLogOut(FRTaskLog):
    task_log: Json


##########################################################################################################################
##########################       ADDITIONAL SCHEMAS       #######################################################################
##########################################################################################################################
class UserResponse(BaseModel):
    exists:bool=False
    grouped:bool=False
    user_details:List=[]

class Message(BaseModel):
    message: str
