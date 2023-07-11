import uvicorn
from backend.fastapi_app import fastapi_app
from config import FASTAPI_HOST, FASTAPI_PORT

# import test

if __name__ == "__main__":
    print("Starting EAI Core API Server!!!")
    uvicorn.run(fastapi_app, host=FASTAPI_HOST, port=FASTAPI_PORT)
    

