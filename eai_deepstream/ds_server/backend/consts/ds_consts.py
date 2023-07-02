from imports import (
    BaseModel
)


class CameraChange(str):
    camera_add = "camera_add"
    camera_remove = "camera_remove"


class CameraRequest(BaseModel):
    camera_id: str
    camera_url: str

class CameraPayload(CameraRequest):
    change:str


class PipelineRequest(BaseModel):
    pipeline_id: str
    pipeline_name: str