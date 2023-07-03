from imports import (
    BaseModel,
    Callable, Optional, Union, Dict,
    DictConfig,
)


class CameraChangeVars(str):
    camera_add = "camera_add"
    camera_remove = "camera_remove"


class CameraRequestVars(BaseModel):
    camera_id: str
    camera_url: str

class CameraPayloadVars(CameraRequestVars):
    change:str


class PipelineBaseVars(BaseModel):
    pipeline_id: str
    pipeline_name: str
    pipeline_props: Union[DictConfig, Dict]

