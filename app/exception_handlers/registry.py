from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import ResponseValidationError

from app.exception_handlers.database import SQLAlchemyExceptionHandler
from app.exception_handlers.validation import ResponseValidationExceptionHandler

def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(SQLAlchemyError, SQLAlchemyExceptionHandler.handle_exception)
    app.add_exception_handler(ResponseValidationError, ResponseValidationExceptionHandler.handle_exception)