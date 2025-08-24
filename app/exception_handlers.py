import orjson
from fastapi import FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from rotoger import AppStructLogger
from sqlalchemy.exc import SQLAlchemyError

logger = AppStructLogger().get_logger()


# TODO: add reasoning for this in readme plus higligh using re-raise in db session
async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
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


async def response_validation_exception_handler(
    request: Request, exc: ResponseValidationError
) -> JSONResponse:
    request_path = request.url.path
    try:
        raw_body = await request.body()
        request_body = orjson.loads(raw_body) if raw_body else None
    except orjson.JSONDecodeError:
        request_body = None

    errors = exc.errors()

    # Check if this is a None/null response case
    is_none_response = False
    for error in errors:
        # Check for null input pattern
        if error.get("input") is None and "valid dictionary" in error.get("msg", ""):
            is_none_response = True
            break

    await logger.aerror(
        "Response validation error occurred",
        validation_errors=errors,
        request_url=request_path,
        request_body=request_body,
        is_none_response=is_none_response,
    )

    if is_none_response:
        # Return 404 when response is None (resource not found)
        return JSONResponse(
            status_code=404,
            content={"no_response": "The requested resource was not found"},
        )
    else:
        # Return 422 when response exists but doesn't match expected format
        return JSONResponse(
            status_code=422,
            content={"response_format_error": errors},
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(
        ResponseValidationError, response_validation_exception_handler
    )
