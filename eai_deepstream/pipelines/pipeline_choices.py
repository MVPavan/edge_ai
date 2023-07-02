from imports import (
    Optional, Union, Type
)
from .pipeline_builds.od_single_head import ODSingleHead
from .pipeline_builds.ds_pipeline_base import DsPipelineBase

class PipelineChoices(str):
    od_single_head = "od_single_head"


class PipelineChoicesManager:
    @staticmethod
    def get_pipeline_choices():
        return PipelineChoices().__dict__
    
    @staticmethod
    def get_pipeline_choice(pipeline_choice:str):
        return PipelineChoices().__dict__[pipeline_choice]
    
    @staticmethod
    def get_pipeline_choice_class(pipeline_choice:str) -> Union[
                Type[ODSingleHead],
                Type[DsPipelineBase]
        ]:
        if pipeline_choice == PipelineChoices.od_single_head:
            return ODSingleHead
        
        raise ValueError(f"Invalid pipeline choice: {pipeline_choice}")
    