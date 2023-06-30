from typing import List
from pydantic import BaseModel
import requests
import uvicorn
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import RedirectResponse

API_V1_STR = "/deepstream/api/v1"


# Sample payload
'''
curl -XPOST 'http://localhost:9000/stream/add' -d '{
    "key": "sensor",
    "value": {
        "camera_id": "uniqueSensorID1",
        "camera_name": "front_door",
        "camera_url": "file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_1080p_h264.mp4",
        "change": "camera_add",
        "metadata": {
            "resolution": "1920 x1080",
            "codec": "h264",
            "framerate": 30
        }
    },
    "headers": {
        "source": "vst",
        "created_at": "2021-06-01T14:34:13.417Z"
    }
}'

'''

class CameraChange(str):
    camera_add = "camera_add"
    camera_remove = "camera_remove"


class CameraRequest(BaseModel):
    camera_id: str
    camera_url: str = "file:///data/datasets/infer/org/videos/ds_test/busy_1080p_12fps.h264"
    class Config:
        orm_mode = True

class CameraPayload(CameraRequest):
    change:str

def create_payload(cam_payload:CameraPayload):
    body = {
        "value": {
            "camera_id": cam_payload.camera_id,
            "camera_url": cam_payload.camera_url,
            "change": cam_payload.change,
        }
    }
    return body


uri_router = APIRouter()

@uri_router.post("/camera_add/")
def add_camera(cam_request: CameraRequest):
    http_url = 'http://localhost:9005/stream/add'
    cam_payload = CameraPayload(**cam_request.dict(), change=CameraChange.camera_add)
    json_body = create_payload(cam_payload=cam_payload)
    response = requests.post(url=http_url, json=json_body)
    return response.status_code, response.json()


@uri_router.post("/camera_remove/")
def remove_camera(cam_request: CameraRequest):
    http_url = 'http://localhost:9005/stream/remove'
    cam_payload = CameraPayload(**cam_request.dict(), change=CameraChange.camera_remove)
    json_body = create_payload(cam_payload=cam_payload)
    response = requests.post(url=http_url, json=json_body)
    return response.status_code, response.json()


# @uri_router.post("/add_multiple_camera/{num_of_cameras}")
# def add_multiple_camera(cam_request: CameraRequest):


def create_app() -> FastAPI:
    _app = FastAPI(title="UllustraAI Gen2 Deepstream", openapi_url=f"{API_V1_STR}/openapi.json")
    _app.include_router(uri_router, prefix=API_V1_STR)

    @_app.get("/")
    async def root(request: Request):
        return RedirectResponse(url="/docs")

    return _app


def start_server():
    fastapi_app = create_app()
    uvicorn.run(fastapi_app, host="0.0.0.0", port=7080)


if __name__ == "__main__":
    start_server()
