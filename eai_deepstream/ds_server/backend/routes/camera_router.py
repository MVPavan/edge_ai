from imports import (
    APIRouter, Depends,  HTTPException
)

import ..consts.ds_consts as DsConsts

camera_router = APIRouter()


# Cameras CRUD
@camera_router.post("/camera_add/", response_model=DsConsts.CameraRequest, tags=["Cameras"])
def add_camera(camera: DsConsts.CameraRequest):
    return camera

@camera_router.post("/camera_remove/", response_model=list[DsConsts.CameraRequest], tags=["Cameras"])
def remove_camera(camera: DsConsts.CameraRequest):
    return camera

@camera_router.post("/roi_update/", response_model=list[DsConsts.CameraRequest], tags=["Cameras"])
def update_roi(camera: DsConsts.CameraRequest):
    return camera

@camera_router.post("/drop_frame_interval/", response_model=list[DsConsts.CameraRequest], tags=["Cameras"])
def update_drop_frame_interval(camera: DsConsts.CameraRequest):
    return camera



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