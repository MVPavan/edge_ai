import uvicorn
from backend.fastapi_app import fastapi_app

# import test

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8090)
    pass


# from backend.tq_jobs.celery_practice import add
# import time
#
#
# def a1(iter):
#     st = time.time()
#     for i in range(iter):
#         add.delay(5, 6)
#     et = time.time()
#     print(et - st)
#
#
# print("here")
