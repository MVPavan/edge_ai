from imports import (
    Dict, Optional, Union,
    BaseModel, validator
)

from ds_consts.server_consts import (
    PipelineChoicesManager,
    PipelineBaseVars,
    PipelineRequestVars,
    PipelineCollectionVars,
    PipelineConstructVars
)




class PipelineManager:
    def __init__(self) -> None:
        self.existing_pipelines:PipelineCollectionVars = PipelineCollectionVars(pipelines={})
        self.pipeline_choice_manager = PipelineChoicesManager()
    
    def add_pipeline(self, pipeline_request_vars:PipelineRequestVars) -> PipelineConstructVars:
        ds_pipeline_class = self.pipeline_choice_manager.get_pipeline_choice_class(
            pipeline_choice=pipeline_request_vars.pipeline_choice
        )
        pipeline_base_vars=PipelineBaseVars(**pipeline_request_vars.dict())
        pipeline_object = ds_pipeline_class(pipeline_base_vars=pipeline_base_vars)

        pipeline_construct = PipelineConstructVars(
            **pipeline_request_vars.dict(),
            pipeline_object=pipeline_object
        )
        self.existing_pipelines.pipelines[pipeline_request_vars.pipeline_id] = pipeline_construct
        return pipeline_construct




















