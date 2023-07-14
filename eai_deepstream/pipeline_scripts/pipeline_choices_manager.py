from imports import (
    Optional, Union, Type
)
from .pipelines.od_single_head import ODSingleHead
from .pipelines.ds_pipeline_base import DsPipelineBase


class PipelineChoicesVars(str):
    od_single_head = "od_single_head"


class PipelineChoicesManager:
    @staticmethod
    def get_pipeline_choices():
        return PipelineChoicesVars().__dict__
    
    @staticmethod
    def get_pipeline_choice(pipeline_choice:str):
        return PipelineChoicesVars().__dict__[pipeline_choice]
    
    @staticmethod
    def get_pipeline_choice_class(pipeline_choice:str) -> Union[
                Type[ODSingleHead],
                Type[DsPipelineBase]
        ]:
        if pipeline_choice == PipelineChoicesVars.od_single_head:
            return ODSingleHead
        
        raise ValueError(f"Invalid pipeline choice: {pipeline_choice}")
    