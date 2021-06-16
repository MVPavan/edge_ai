from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from app.api.api_v1.api import api_router
from app.core import config
from app.db.utils.db_inits import (
    connect_to_pgdb,
    connect_to_mongo,
    close_mongo_connection,
    # close_pgdb_session,
)


def create_app() -> FastAPI:
    app = FastAPI(title=config.PROJECT_NAME, openapi_url="/api/v1/openapi.json")
    app.add_event_handler("startup", connect_to_pgdb)
    app.add_event_handler("startup", connect_to_mongo)
    app.add_event_handler("shutdown", close_mongo_connection)
    # app.add_event_handler("shutdown", close_pgdb_session)
    app.include_router(api_router, prefix=config.API_V1_STR)
    return app


app = create_app()
