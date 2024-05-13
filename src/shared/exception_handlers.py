import traceback

from starlette.responses import JSONResponse

from shared.common_schemas import OutputDataDTO
from config import DEBUG


async def validation_exception_handler(request, exc):
    response = OutputDataDTO(
        success=False,
        details=exc.errors()
    )
    return JSONResponse(response.dict(), status_code=406)


async def http_exception_handler(request, exc):
    response = OutputDataDTO(
        success=False,
        details=exc.detail
    )
    return JSONResponse(response.dict(), status_code=exc.status_code)


async def general_exception_handler(request, exc: Exception):
    msg = traceback.format_stack() if DEBUG else 'Internal server error'
    response = OutputDataDTO(
        success=False,
        details=msg
    )
    return JSONResponse(response.dict(), status_code=500)
