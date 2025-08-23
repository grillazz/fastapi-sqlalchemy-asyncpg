from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import orjson
from fastapi import FastAPI
from rotoger import AppStructLogger

logger = AppStructLogger().get_logger()

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    request_path = request.url.path
    try:
        raw_body = await request.body()
        request_body = orjson.loads(raw_body) if raw_body else None
    except orjson.JSONDecodeError:
        request_body = None

    await logger.aerror(
        "Database error occurred",
        sql_error=repr(exc),
        request_url=request_path,
        request_body=request_body,
    )

    return JSONResponse(
        status_code=500,
        content={"message": "A database error occurred. Please try again later."},
    )

def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
