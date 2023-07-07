from imports import (
    APIRouter, Depends,  HTTPException,
    requests
)

import ds_consts.camera_consts as CamVars
from pipeline_scripts.pipeline_manager import get_pipeline_manager, PipelineManager

from .route_utils import (
    check_pipeline_exists_router, 
    get_mutltiurisrcbin_url,
    payload_generator
)

cam_router = APIRouter()


# Cameras CRUD
@cam_router.post("/camera_add/", response_model=CamVars.CameraRequestVars, tags=["DSPCameras"])
def add_camera(
    cam_request: CamVars.CameraRequestVars, 
    pipeline_manager: PipelineManager = Depends(get_pipeline_manager)
  ):
    pipeline_response = check_pipeline_exists_router(cam_request.pipeline_id, pipeline_manager)
    http_url = get_mutltiurisrcbin_url(
        pipeline_id=cam_request.pipeline_id, 
        camera_action=CamVars.CameraAction.camera_add,
        pipeline_manager=pipeline_manager
    )
    payload = payload_generator(cam_request, CamVars.CameraAction.camera_add)
    response = requests.post(http_url, json=payload)
    return response.status_code, response.json()


@cam_router.post("/camera_remove/", response_model=CamVars.CameraRequestVars, tags=["DSPCameras"])
def remove_camera(
    cam_request: CamVars.CameraRequestVars, 
    pipeline_manager: PipelineManager = Depends(get_pipeline_manager)
  ):
    pipeline_response = check_pipeline_exists_router(cam_request.pipeline_id, pipeline_manager)
    http_url = get_mutltiurisrcbin_url(
        pipeline_id=cam_request.pipeline_id, 
        camera_action=CamVars.CameraAction.camera_remove,
        pipeline_manager=pipeline_manager
    )
    payload = payload_generator(cam_request, CamVars.CameraAction.camera_remove)
    response = requests.post(http_url, json=payload)
    return response.status_code, response.json()


@cam_router.post("/update_roi/", response_model=CamVars.CameraRequestVars, tags=["DSPCameras"])
def update_roi(
    cam_request: CamVars.CameraRequestVars, 
    pipeline_manager: PipelineManager = Depends(get_pipeline_manager)
  ):
    pipeline_response = check_pipeline_exists_router(cam_request.pipeline_id, pipeline_manager)
    http_url = get_mutltiurisrcbin_url(
        pipeline_id=cam_request.pipeline_id, 
        camera_action=CamVars.CameraAction.update_roi,
        pipeline_manager=pipeline_manager
    )
    payload = payload_generator(cam_request, CamVars.CameraAction.update_roi)
    response = requests.post(http_url, json=payload)
    return response.status_code, response.json()


@cam_router.post("/drop_frame_interval/", response_model=CamVars.CameraRequestVars, tags=["DSPCameras"])
def update_drop_frame_interval(
    cam_request: CamVars.CameraRequestVars, 
    pipeline_manager: PipelineManager = Depends(get_pipeline_manager)
  ):
    pipeline_response = check_pipeline_exists_router(cam_request.pipeline_id, pipeline_manager)
    http_url = get_mutltiurisrcbin_url(
        pipeline_id=cam_request.pipeline_id, 
        camera_action=CamVars.CameraAction.drop_frame_interval,
        pipeline_manager=pipeline_manager
    )
    payload = payload_generator(cam_request, CamVars.CameraAction.drop_frame_interval)
    response = requests.post(http_url, json=payload)
    return response.status_code, response.json()



'''
Supported MultiUriApi's in Deepstream 6.2:

1. Stream add/remove
  a. Stream add

  Endpoint: /stream/add
  Curl command to add stream:

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


  Expected output: The uri specified should be added to the display.
  Note: The camera_id should be unique for each newly added streams.

  b. Stream remove

  Endpoint: /stream/remove
  Curl command to remove stream:

  curl -XPOST 'http://localhost:9000/stream/remove' -d '{
    "key": "sensor",
    "value": {
        "camera_id": "uniqueSensorID1",
        "camera_name": "front_door",
        "camera_url": "file:///opt/nvidia/deepstream/deepstream/samples/streams/sample_1080p_h264.mp4",
        "change": "camera_remove",
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

  Expected output: The uri specified should be removed from the display.
  Note: The camera_id used to remove stream should be same as being used while adding stream using REST API.

2. ROI

  Endpoint: /roi/update
  Curl command to update ROI:

  curl -XPOST 'http://localhost:9000/roi/update' -d '{
    "stream": {
        "stream_id": "0",
        "roi_count": 2,
        "roi": [{
                "roi_id": "0",
                "left": 100,
                "top": 300,
                "width": 400,
                "height": 400
            },
            {
                "roi_id": "1",
                "left": 550,
                "top": 300,
                "width": 500,
                "height": 500
            }
        ]
    }
  }'

  Expected output: The updated roi dimension should be observed at display.

3. Decoder

  Endpoint: /dec/drop-frame-interval
  Curl command to configure decoder drop-frame-interval property:

  curl -XPOST 'http://localhost:9000/dec/drop-frame-interval' -d '{
  "stream":
    {
        "stream_id":"0",
        "drop_frame_interval":2
    }
  }'

  Expected output: The drop-frame-interval value will be set on the decoder.
  Decoder drop frame interval should reflect with every interval <value> frame
  given by decoder, rest all dropped for selected stream.

4. Nvinfer

  Endpoint: /infer/set-interval
  Curl command to configure nvinfer interval property:

  curl -XPOST 'http://localhost:9000/infer/set-interval' -d '{
  "stream":
    {
        "stream_id":"0",
        "interval":2
    }
  }'

  Expected output: The interval value will be set on the nvinfer.
  Interval value specify consecutive batches will be skipped for inference for
  the video stream.

  Note: Disable/comment "input-tensor-meta" property in dsserver_pgie_config.yml
  to see "interval" property functionality of nvinfer.
  Currently stream_id (specified in the schema) do not have any impact on specified
  stream_id, rather configuration is getting applied to all active streams.
'''