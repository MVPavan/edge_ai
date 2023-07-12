
from eai_core_api.imports import (
    BaseModel,
    Callable, Optional, Union, Dict,
    DictConfig, validator
)

from .base_consts import (
    PipelineBaseVars,
)

from pipeline_scripts.pipeline_choices_manager import (
    PipelineChoicesManager,
    ODSingleHead,
    DsPipelineBase
)

class PipelineRequestVars(PipelineBaseVars):
    pipeline_choice: str

    @validator("pipeline_choice")
    def validate_pipeline_choice(cls, pipeline_choice):
        if pipeline_choice not in PipelineChoicesManager.get_pipeline_choices():
            raise ValueError(f"Invalid pipeline choice: {pipeline_choice}")
        return pipeline_choice
    

class PipelineConstructStatus(str):
    success = "success"
    failure = "failure"
    id_exists = "id_exists"
    does_not_exist = "does_not_exist"

class PipelineResponseVars(PipelineBaseVars):
    pipeline_choice: str
    status:str = PipelineConstructStatus.failure

class PipelineConstructVars(PipelineRequestVars):
    pipeline_object:Union[
        ODSingleHead,
        DsPipelineBase
    ]
            
class PipelineCollectionVars(BaseModel):
    pipelines: Dict[str, PipelineConstructVars]