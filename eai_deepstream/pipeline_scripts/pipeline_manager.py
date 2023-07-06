from imports import (
    Dict, Optional, Union,
    BaseModel, validator
)

from ds_consts.server_consts import (
    PipelineChoicesManager,
    PipelineBaseVars,
    PipelineRequestVars,
    PipelineCollectionVars,
    PipelineConstructVars,
    PipelineConstructStatus
)


class PipelineManager:
    def __init__(self) -> None:
        self.existing_pipelines:PipelineCollectionVars = PipelineCollectionVars(pipelines={})
        self.pipeline_choice_manager = PipelineChoicesManager()
    
    def add_pipeline(self, pipeline_request_vars:PipelineRequestVars) -> PipelineConstructVars:
        
        if pipeline_request_vars.pipeline_id in self.existing_pipelines.pipelines:
            pipeline_construct = PipelineConstructVars(
                **pipeline_request_vars.dict(),
                status=PipelineConstructStatus.id_exists
            )
            return pipeline_construct
        
        ds_pipeline_class = self.pipeline_choice_manager.get_pipeline_choice_class(
            pipeline_choice=pipeline_request_vars.pipeline_choice
        )
        pipeline_base_vars=PipelineBaseVars(**pipeline_request_vars.dict())

        # create pipeline object
        pipeline_object = ds_pipeline_class(pipeline_base_vars=pipeline_base_vars)

        pipeline_construct = PipelineConstructVars(
            **pipeline_request_vars.dict(),
            pipeline_object=pipeline_object,
            status=PipelineConstructStatus.success
        )
        # add pipeline object to pipeline collection
        self.existing_pipelines.pipelines[pipeline_request_vars.pipeline_id] = pipeline_construct
        return pipeline_construct
    

    def delete_pipeline(self, pipeline_id:str) -> bool:
        
        pipeline_construct = self.existing_pipelines.pipelines[pipeline_id]
        if pipeline_construct.pipeline_object is not None:
            if pipeline_construct.pipeline_object.stop_pipeline():
                del pipeline_construct
                self.existing_pipelines.pipelines.pop(pipeline_id)
                return True
        return False

pipeline_manager = None
def get_pipeline_manager() -> PipelineManager:
    global pipeline_manager
    if pipeline_manager is None:
        pipeline_manager = PipelineManager()
    return pipeline_manager

















