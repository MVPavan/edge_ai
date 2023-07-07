from imports import (
    BaseModel,
    Callable, Optional, Union, Dict,
    DictConfig,
)

from .base_consts import CameraAction

class CameraRequestVars(BaseModel):
    camera_id: str
    camera_url: str
    pipeline_id: str

class CameraPayloadVars(CameraRequestVars):
    change:str = CameraAction.camera_add



