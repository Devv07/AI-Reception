from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _make_json_safe(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    if isinstance(value, dict):
        return {key: _make_json_safe(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_make_json_safe(item) for item in value]

    if isinstance(value, tuple):
        return [_make_json_safe(item) for item in value]

    return value


def _error_response(
    message: str,
    status_code: int,
    details: object | None = None,
) -> JSONResponse:
    payload = {"success": False, "error": {"message": message}}

    if details is not None:
        payload["error"]["details"] = _make_json_safe(details)

    return JSONResponse(
        status_code=status_code,
        content=payload,
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return _error_response(str(exc.detail), exc.status_code)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        "Request validation failed",
        422,
        _make_json_safe(exc.errors()),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return _error_response("Internal server error", 500)