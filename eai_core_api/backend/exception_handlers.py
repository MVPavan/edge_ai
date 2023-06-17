from imports import (
    PlainTextResponse,
    JSONResponse,
)



class ExceptionHandlers:
    @staticmethod
    async def validation_exception_handler(request, exc):
        return PlainTextResponse(str(exc), status_code=400)

    @staticmethod
    async def value_error_exception_handler(request, exc: ValueError):
        return PlainTextResponse(str(exc), status_code=400)
        # return JSONResponse(
        #     status_code=400,
        #     content={"message": str(exc)},
        # )

    @staticmethod
    async def assertion_error_exception_handler(request, exc: AssertionError):
        return PlainTextResponse(str(exc), status_code=400)

    @staticmethod
    async def type_error_exception_handler(request, exc: TypeError):
        return PlainTextResponse(str(exc), status_code=400)

