from imports import (
    APIRouter, Depends,  HTTPException,
    List
)

import ds_consts.server_consts as DsServerConsts

from pipeline_scripts.pipeline_manager import get_pipeline_manager, PipelineManager

pipeline_router = APIRouter()

# Pipeline CRUD
@pipeline_router.post("/add_pipeline/", response_model=DsServerConsts.PipelineResponseVars, tags=["Pipelines"])
def add_pipeline(
    pipeline: DsServerConsts.PipelineRequestVars, 
    pipeline_manager: PipelineManager = Depends(get_pipeline_manager)
    ):
    pipeline_construct = pipeline_manager.add_pipeline(pipeline)
    if pipeline_construct.status == DsServerConsts.PipelineConstructStatus.id_exists:
        raise HTTPException(status_code=400, detail=f"Pipeline with id {pipeline.pipeline_id} already exists")
    return pipeline_construct

@pipeline_router.get("/get_pipeline/{pipeline_id}", response_model=DsServerConsts.PipelineResponseVars, tags=["Pipelines"])
def get_pipeline(pipeline_id: str, pipeline_manager: PipelineManager = Depends(get_pipeline_manager)):
    if pipeline_id not in pipeline_manager.existing_pipelines.pipelines:
        raise HTTPException(status_code=404, detail=f"Pipeline with id {pipeline_id} not found")
    return DsServerConsts.PipelineResponseVars(**pipeline_manager.existing_pipelines.pipelines[pipeline_id].dict())

@pipeline_router.get("/get_all_pipelines/", response_model=List[DsServerConsts.PipelineResponseVars], tags=["Pipelines"])
def get_all_pipelines(pipeline_manager: PipelineManager = Depends(get_pipeline_manager)):
    return [
        DsServerConsts.PipelineResponseVars(**pipeline_manager.existing_pipelines.pipelines[pipeline_id].dict()) 
        for pipeline_id in pipeline_manager.existing_pipelines.pipelines
    ]

@pipeline_router.delete("/delete_pipeline/{pipeline_id}", response_model=DsServerConsts.PipelineResponseVars, tags=["Pipelines"])
def delete_pipeline(pipeline_id: str, pipeline_manager: PipelineManager = Depends(get_pipeline_manager)):
    if pipeline_id not in pipeline_manager.existing_pipelines.pipelines:
        raise HTTPException(status_code=404, detail=f"Pipeline with id {pipeline_id} not found")
    response = DsServerConsts.PipelineResponseVars(**pipeline_manager.existing_pipelines.pipelines[pipeline_id].dict())
    if not pipeline_manager.delete_pipeline(pipeline_id):
        raise HTTPException(status_code=400, detail=f"Pipeline with id {pipeline_id} could not be deleted")
    return response


# Pipeline Choices
@pipeline_router.get("/get_pipeline_choices/", response_model=List[str], tags=["Pipelines"])
def get_pipeline_choices(pipeline_manager: PipelineManager = Depends(get_pipeline_manager)):
    return list(pipeline_manager.pipeline_choice_manager.get_pipeline_choices().keys())