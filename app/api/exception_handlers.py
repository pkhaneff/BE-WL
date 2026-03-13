from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DomainError,
    ApplicationError,
    InfrastructureError,
    InvalidTokenError,
    NotFoundError,
    PermissionDeniedError,
    ConflictError,
    ValidationError,
)


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    if isinstance(exc, NotFoundError):
        status_code = 404
    elif isinstance(exc, PermissionDeniedError):
        status_code = 403
    elif isinstance(exc, ConflictError):
        status_code = 409
    else:
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    if isinstance(exc, ValidationError):
        status_code = 422
    else:
        status_code = 400
    return JSONResponse(
        status_code=status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def infrastructure_error_handler(
    request: Request, exc: InfrastructureError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"code": exc.code, "message": "Dịch vụ tạm thời không khả dụng."},
    )


async def invalid_token_handler(request: Request, exc: InvalidTokenError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"code": exc.code, "message": exc.message},
    )
