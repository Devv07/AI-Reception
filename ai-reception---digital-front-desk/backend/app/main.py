from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import router
from app.core.config import get_settings
from app.core.exceptions import http_exception_handler, unhandled_exception_handler, validation_exception_handler
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()
app = FastAPI(title="AI Reception Backend", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def request_size_limit(request: Request, call_next):
	content_length = request.headers.get("content-length")
	if content_length:
		try:
			content_length_value = int(content_length)
		except ValueError:
			return JSONResponse(status_code=400, content={"success": False, "error": {"message": "Invalid Content-Length header"}})
		if content_length_value < 0:
			return JSONResponse(status_code=400, content={"success": False, "error": {"message": "Invalid Content-Length header"}})
		if content_length_value > settings.max_request_bytes:
			return JSONResponse(status_code=413, content={"success": False, "error": {"message": "Request body is too large"}})
	return await call_next(request)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(router)
