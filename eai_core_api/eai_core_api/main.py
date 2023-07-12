import uvicorn
from eai_core_api.backend.fastapi_app import fastapi_app
from eai_core_api.config import FASTAPI_HOST, FASTAPI_PORT

# import test

if __name__ == "__main__":
    print("Starting EAI Core API Server!!!")
    uvicorn.run(fastapi_app, host=FASTAPI_HOST, port=FASTAPI_PORT)
    

