from imports import (
    APIRouter, Depends,  HTTPException
)

import ds_server.backend.consts.ds_consts as DsConsts

from eai_deepstream.pipelines.pipeline_manager import PipelineManager

pipeline_router = APIRouter()

# Pipeline CRUD
@pipeline_router.post("/pipeline_add/", response_model=DsConsts.PipelineRequest, tags=["Pipelines"])
def add_pipeline(pipeline: DsConsts.PipelineRequest):
