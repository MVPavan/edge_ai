from fastapi import APIRouter
from app.api.api_v1.routes import groups, users, fr_ops

api_router = APIRouter()
api_router.include_router(
    groups.group_router,
    prefix="/groups",
    tags=["Groups"],
    responses={404: {"description": "Not found"}},
)
api_router.include_router(
    users.user_router,
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)
api_router.include_router(
    fr_ops.fr_ops_router,
    prefix="/face",
    tags=["Face"],
    responses={404: {"description": "Not found"}},
)
