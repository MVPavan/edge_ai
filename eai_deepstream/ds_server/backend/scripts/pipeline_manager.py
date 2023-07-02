from imports import (
    Dict, Optional, Union,
    BaseModel, validator
)

from pipelines.pipeline_builds.ds_pipeline_base import DsPipelineBase, DsPipelineProps
from pipelines.pipeline_choices import (
    PipelineChoicesManager,
    ODSingleHead
)

class PipelineBase(BaseModel):
    pipeline_id: str
    pipeline_name: str
    pipeline_choice: str
    pipeline_props: DsPipelineProps

    @validator("pipeline_choice")
    def validate_pipeline_choice(cls, pipeline_choice):
        if pipeline_choice not in PipelineChoicesManager.get_pipeline_choices():
            raise ValueError(f"Invalid pipeline choice: {pipeline_choice}")
        return pipeline_choice


class PipelineConstruct(PipelineBase):
    pipeline_object:Union[
        ODSingleHead,
        DsPipelineBase
    ]
            
class PipelineCollection(BaseModel):
    pipelines: Dict[str, PipelineConstruct]


class PipelineManager:
    def __init__(self) -> None:
        self.existing_pipelines:PipelineCollection = PipelineCollection(pipelines={})
        self.pipeline_choice_manager = PipelineChoicesManager()
    
    def add_pipeline(self, pipeline_base:PipelineBase) -> PipelineConstruct:
        ds_pipeline_class = self.pipeline_choice_manager.get_pipeline_choice_class(
            pipeline_choice=pipeline_base.pipeline_choice
        )
        pipeline_object = ds_pipeline_class(
            ds_pipeline_props=pipeline_base.pipeline_props
        )

        pipeline_construct = PipelineConstruct(
            **pipeline_base.dict(),
            pipeline_object=pipeline_object
        )
        self.existing_pipelines.pipelines[pipeline_base.pipeline_id] = pipeline_construct
        return pipeline_construct




















