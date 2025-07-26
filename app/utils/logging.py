import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import orjson
import structlog
from attrs import define, field
from whenever._whenever import Instant

from app.utils.singleton import SingletonMetaNoArgs


class RotatingBytesLogger:
    """Logger that respects RotatingFileHandler's rotation capabilities."""

    def __init__(self, handler):
        self.handler = handler

    def msg(self, message):
        """Process a message and pass it through the handler's emit method."""
        if isinstance(message, bytes):
            message = message.decode("utf-8")

        # Create a log record that will trigger rotation checks
        record = logging.LogRecord(
            name="structlog",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=message.rstrip("\n"),
            args=(),
            exc_info=None
        )

        # Check if rotation is needed before emitting
        if self.handler.shouldRollover(record):
            self.handler.doRollover()

        # Emit the record through the handler
        self.handler.emit(record)

    # Required methods to make it compatible with structlog
    def debug(self, message):
        self.msg(message)

    def info(self, message):
        self.msg(message)

    def warning(self, message):
        self.msg(message)

    def error(self, message):
        self.msg(message)

    def critical(self, message):
        self.msg(message)


class RotatingBytesLoggerFactory:
    """Factory that creates loggers that respect file rotation."""

    def __init__(self, handler):
        self.handler = handler

    def __call__(self, *args, **kwargs):
        return RotatingBytesLogger(self.handler)


@define
class AppStructLogger(metaclass=SingletonMetaNoArgs):
    _logger: structlog.BoundLogger = field(init=False)

    def __attrs_post_init__(self):
        _log_date = Instant.now().py_datetime().strftime("%Y%m%d")
        _log_path = Path(f"{_log_date}_{os.getpid()}.log")
        _handler = RotatingFileHandler(
            filename=_log_path,
            maxBytes=1000,
            backupCount=5,
            encoding="utf-8"
        )
        structlog.configure(
            cache_logger_on_first_use=True,
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.format_exc_info,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.JSONRenderer(serializer=orjson.dumps),
            ],
            logger_factory=RotatingBytesLoggerFactory(_handler)
        )
        self._logger = structlog.get_logger()

    def get_logger(self) -> structlog.BoundLogger:
        return self._logger
