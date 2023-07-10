# Base constants for the DeepStream pipeline
# These constants are used by the DeepStream server and the DeepStream pipeline scripts
# keep them seperate to avoid circular imports

from imports import (
    BaseModel,
    Callable, Optional, Union, Dict,
    DictConfig,
)


class CameraAction(str):
    camera_add = "camera_add"
    camera_remove = "camera_remove"
    update_roi = "update_roi"
    drop_frame_interval = "drop_frame_interval"

class PipelineBaseVars(BaseModel):
    pipeline_id: str
    pipeline_name: str
    pipeline_props: Dict