# app/exception_handlers/base.py
import orjson
from fastapi import Request
from fastapi.responses import JSONResponse
from rotoger import AppStructLogger

logger = AppStructLogger().get_logger()


class BaseExceptionHandler:
    """Base class for all exception handlers with common functionality."""

    @staticmethod
    async def extract_request_info(request: Request):
        """Extract common request information."""
        request_path = request.url.path
        try:
            raw_body = await request.body()
            request_body = orjson.loads(raw_body) if raw_body else None
        except orjson.JSONDecodeError:
            request_body = None

        return request_path, request_body

    @classmethod
    async def log_error(cls, message, request_info, **kwargs):
        """Log error with standardized format."""
        request_path, request_body = request_info
        await logger.aerror(
            message,
            request_url=request_path,
            request_body=request_body,
            **kwargs
        )