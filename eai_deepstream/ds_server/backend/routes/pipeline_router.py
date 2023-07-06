from imports import (
    APIRouter, Depends,  HTTPException,
    List
)

import ds_consts.pipeline_consts as DsPipelineConsts

from pipeline_scripts.pipeline_manager import get_pipeline_manager, PipelineManager

pipeline_router = APIRouter()

# Pipeline CRUD
@pipeline_router.post("/add_pipeline/", response_model=DsPipelineConsts.PipelineResponseVars, tags=["Pipelines"])
def add_pipeline(
    pipeline: DsPipelineConsts.PipelineRequestVars, 
    pipeline_manager: PipelineManager = Depends(get_pipeline_manager)
    ):
    pipeline_response = pipeline_manager.add_pipeline(pipeline)
    if pipeline_response.status == DsPipelineConsts.PipelineConstructStatus.id_exists:
        raise HTTPException(status_code=400, detail=f"Pipeline with id {pipeline.pipeline_id} already exists")
    return pipeline_response

@pipeline_router.get("/get_pipeline/{pipeline_id}", response_model=DsPipelineConsts.PipelineResponseVars, tags=["Pipelines"])
def get_pipeline(pipeline_id: str, pipeline_manager: PipelineManager = Depends(get_pipeline_manager)):
    pipeline_response = pipeline_manager.check_pipeline_exists(pipeline_id)
    if pipeline_response.status == DsPipelineConsts.PipelineConstructStatus.does_not_exist:
        raise HTTPException(status_code=404, detail=f"Pipeline with id {pipeline_id} not found")
    return pipeline_response

@pipeline_router.get("/get_all_pipelines/", response_model=List[DsPipelineConsts.PipelineResponseVars], tags=["Pipelines"])
def get_all_pipelines(pipeline_manager: PipelineManager = Depends(get_pipeline_manager)):
    return [
        pipeline_manager.check_pipeline_exists(pipeline_id) for pipeline_id in pipeline_manager.existing_pipelines.pipelines
    ]

@pipeline_router.delete("/delete_pipeline/{pipeline_id}", response_model=DsPipelineConsts.PipelineResponseVars, tags=["Pipelines"])
def delete_pipeline(pipeline_id: str, pipeline_manager: PipelineManager = Depends(get_pipeline_manager)):
    pipeline_response = pipeline_manager.delete_pipeline(pipeline_id)
    if pipeline_response.status == DsPipelineConsts.PipelineConstructStatus.does_not_exist:
        raise HTTPException(status_code=404, detail=f"Pipeline with id {pipeline_id} not found")
    elif pipeline_response.status == DsPipelineConsts.PipelineConstructStatus.failure:
        raise HTTPException(status_code=400, detail=f"Pipeline with id {pipeline_id} could not be deleted")
    return pipeline_response


# Pipeline Choices
@pipeline_router.get("/get_pipeline_choices/", response_model=List[str], tags=["Pipelines"])
def get_pipeline_choices(pipeline_manager: PipelineManager = Depends(get_pipeline_manager)):
    return list(pipeline_manager.pipeline_choice_manager.get_pipeline_choices().keys())