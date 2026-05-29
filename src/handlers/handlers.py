from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions import AppException

# This function below handlers all the custom exception class that I have made.
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message
        }
    )
