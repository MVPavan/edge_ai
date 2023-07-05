import uvicorn
from backend.fastapi_app import fastapi_app

# import test

if __name__ == "__main__":
    print("Starting EAI Core API Server!!")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8090)
    

