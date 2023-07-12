from eai_core_api.imports import (
    FastAPI, Request, RedirectResponse,
    RequestValidationError
)


from pipeline_scripts.pipeline_manager import get_pipeline_manager
from .routes.api_router_aggregate import api_router
from .exception_handlers import ExceptionHandlers



API_V1_STR = "/edgeai/deepstream/v1"

def create_app() -> FastAPI:
    _app = FastAPI(title="EdgeAI Deepstream", openapi_url=f"{API_V1_STR}/openapi.json")
    _app.add_event_handler("startup", get_pipeline_manager)

    _app.add_exception_handler(RequestValidationError, ExceptionHandlers.validation_exception_handler)
    _app.add_exception_handler(ValueError, ExceptionHandlers.value_error_exception_handler)
    _app.add_exception_handler(AssertionError, ExceptionHandlers.assertion_error_exception_handler)
    _app.add_exception_handler(TypeError, ExceptionHandlers.type_error_exception_handler)

    _app.include_router(api_router, prefix=API_V1_STR)

    @_app.get("/")
    async def root(request: Request):
        return RedirectResponse(url="/docs")

    return _app

fastapi_app = create_app()
