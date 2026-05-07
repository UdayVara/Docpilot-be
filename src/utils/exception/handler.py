# src/utils/exceptions/handler.py

from fastapi import Request
from fastapi.responses import JSONResponse

from src.utils.exception.custom_exception import CustomException


async def custom_exception_handler(
    request: Request,
    exc: CustomException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "statusCode": exc.status_code,
            "message": exc.message,
            "data": exc.data
        },
    )