from eai_core_api.imports import (
    Depends, HTTPException
)

from pipeline_scripts.pipeline_manager import get_pipeline_manager, PipelineManager
import ds_consts.pipeline_consts as DsPipelineConsts
import ds_consts.camera_consts as CamVars

def check_pipeline_exists_router(pipeline_id: str, pipeline_manager: PipelineManager):
    pipeline_response = pipeline_manager.check_pipeline_exists(pipeline_id)
    if pipeline_response.status == DsPipelineConsts.PipelineConstructStatus.does_not_exist:
        raise HTTPException(status_code=404, detail=f"Pipeline with id {pipeline_id} not found")
    return pipeline_response

def get_mutltiurisrcbin_url(pipeline_id:str, camera_action:str, pipeline_manager:PipelineManager):
    port = pipeline_manager.pipeline_port_map[pipeline_id]
    http_url = f"http://localhost:{port}"
    if camera_action.lower() == CamVars.CameraAction.camera_add:
        http_url = f"{http_url}/stream/add"
    elif camera_action.lower() == CamVars.CameraAction.camera_remove:
        http_url = f"{http_url}/stream/remove"
    elif camera_action.lower() == CamVars.CameraAction.update_roi:
        http_url = f"{http_url}/roi/update"
    elif camera_action.lower() == CamVars.CameraAction.drop_frame_interval:
        http_url = f"{http_url}/dec/drop-frame-interval"
    else:
        raise HTTPException(status_code=400, detail=f"Invalid camera action {camera_action}")
    return http_url

def payload_generator(camera_request:CamVars.CameraRequestVars, camera_action:str):
    if (
        camera_action.lower() == CamVars.CameraAction.camera_add or 
        camera_action.lower() == CamVars.CameraAction.camera_remove
    ):
        payload = {
            "value": {
                "camera_id": camera_request.camera_id,
                "camera_url": camera_request.camera_url,
                "change": camera_action.lower(),
            }
        }
    elif camera_action.lower() == CamVars.CameraAction.update_roi:
        payload = {
            "value": {
                "stream_id": camera_request.camera_id,
                "roi": "", # TODO: Add roi
            }
        }
    elif camera_action.lower() == CamVars.CameraAction.drop_frame_interval:
        payload = {
            "value": {
                "stream_id": camera_request.camera_id,
                "drop-frame-interval": 0, # TODO: Add drop-frame-interval
            }
        }
    else:
        raise HTTPException(status_code=400, detail=f"Invalid camera action: {camera_action}")
    return payload