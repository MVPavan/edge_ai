from imports import APIRouter
from .camera_router import cam_router
from .pipeline_router import dsp_router

api_router = APIRouter()

api_router.include_router(
    dsp_router,
    prefix="/dspipelines",
    # tags=["AI"],
    responses={404: {"description": "Not found"}},
)

api_router.include_router(
    cam_router,
    prefix="/dsp_cameras",
    # tags=["Infrastructure"],
    responses={404: {"description": "Not found"}},
)