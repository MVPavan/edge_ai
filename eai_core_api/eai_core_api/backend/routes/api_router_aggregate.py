from eai_core_api.imports import APIRouter
from .ai_api_router import ai_router
from .infra_api_router import infra_router

api_router = APIRouter()

api_router.include_router(
    ai_router,
    prefix="/ai",
    # tags=["AI"],
    responses={404: {"description": "Not found"}},
)

api_router.include_router(
    infra_router,
    prefix="/infrastructure",
    # tags=["Infrastructure"],
    responses={404: {"description": "Not found"}},
)