from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.exception_handlers.base import BaseExceptionHandler


class SQLAlchemyExceptionHandler(BaseExceptionHandler):
    """Handles SQLAlchemy database exceptions."""

    @classmethod
    async def handle_exception(
        cls, request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        request_info = await cls.extract_request_info(request)

        await cls.log_error(
            "Database error occurred", request_info, sql_error=repr(exc)
        )

        return JSONResponse(
            status_code=500,
            content={"message": "A database error occurred. Please try again later."},
        )
