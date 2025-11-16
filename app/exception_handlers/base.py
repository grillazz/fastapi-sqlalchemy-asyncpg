import orjson
from attrs import define, field
from fastapi import Request
from rotoger import get_logger

logger = get_logger()


@define(slots=True)
class RequestInfo:
    """Contains extracted request information."""

    path: str = field()
    body: dict = field(default=None)


@define(slots=True)
class BaseExceptionHandler:
    """Base class for all exception handlers with common functionality."""

    @staticmethod
    async def extract_request_info(request: Request) -> RequestInfo:
        """Extract common request information."""
        request_path = request.url.path
        request_body = None
        try:
            raw_body = await request.body()
            if raw_body:
                request_body = orjson.loads(raw_body)
        except orjson.JSONDecodeError:
            pass

        return RequestInfo(path=request_path, body=request_body)

    @classmethod
    async def log_error(cls, message: str, request_info: RequestInfo, **kwargs):
        """Log error with standardized format."""
        await logger.aerror(
            message,
            request_url=request_info.path,
            request_body=request_info.body,
            **kwargs,
        )
