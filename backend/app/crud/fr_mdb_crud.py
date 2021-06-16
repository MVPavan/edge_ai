from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId
from pathlib import Path
from pydantic import Json
from app.db.utils.mdb_utils import MongoClient, logger
from app.db.models.fr_mdb_models import mongodb_name, MDBCollections
from app.db.schemas.fr_mdb_schemas import TaskLogBase

#############################################################################################################################################################
####################              TASK LOG CRUD                        ########################################
#############################################################################################################################################################


def get_task_log_by_oid(conn: MongoClient, oid: str) -> TaskLogBase:
    row = conn[mongodb_name][MDBCollections.fr_logs].find_one({"_id": ObjectId(oid)})
    if row:
        return TaskLogBase(**row)


def insert_task_log(conn: MongoClient, task_log: Json) -> TaskLogBase:
    task_log_row = TaskLogBase(task_log=task_log)
    row = conn[mongodb_name][MDBCollections.fr_logs].insert_one(task_log_row.dict())
    if row:
        task_log_row.oid = str(row.inserted_id)
    else:
        logger.info("Error in creating task log!!!")
    return task_log_row


def update_task_log_by_oid(
    conn: MongoClient, oid: str, result_log: Json
) -> TaskLogBase:
    task_log_row = conn[mongodb_name][MDBCollections.fr_logs].update_one(
        {"_id": ObjectId(oid)}, {"$set": {"task_log": result_log}}
    )
    return task_log_row
