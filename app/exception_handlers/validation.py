from fastapi import Request
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse

from app.exception_handlers.base import BaseExceptionHandler


class ResponseValidationExceptionHandler(BaseExceptionHandler):
    """Handles response validation exceptions."""

    @classmethod
    async def handle_exception(
        cls, request: Request, exc: ResponseValidationError
    ) -> JSONResponse:
        request_info = await cls.extract_request_info(request)
        errors = exc.errors()

        # Check if this is a None/null response case
        is_none_response = False
        for error in errors:
            if error.get("input") is None and "valid dictionary" in error.get(
                "msg", ""
            ):
                is_none_response = True
                break

        await cls.log_error(
            "Response validation error occurred",
            request_info,
            validation_errors=errors,
            is_none_response=is_none_response,
        )

        if is_none_response:
            return JSONResponse(
                status_code=404,
                content={"no_response": "The requested resource was not found"},
            )
        else:
            return JSONResponse(
                status_code=422, content={"response_format_error": errors}
            )
