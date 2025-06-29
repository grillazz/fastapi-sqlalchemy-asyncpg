import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import orjson
import structlog
from whenever._whenever import Instant

from app.utils.singleton import SingletonMetaNoArgs


# TODO: merge this wrapper with the one in structlog under one hood of AppLogger
class BytesToTextIOWrapper:
    def __init__(self, handler, encoding="utf-8"):
        self.handler = handler
        self.encoding = encoding

    def write(self, b):
        if isinstance(b, bytes):
            self.handler.stream.write(b.decode(self.encoding))
        else:
            self.handler.stream.write(b)
        self.handler.flush()

    def flush(self):
        self.handler.flush()

    def close(self):
        self.handler.close()

# @define
class AppStructLogger(metaclass=SingletonMetaNoArgs):
    _logger = None

    def __init__(self):
        _log_date = Instant.now().py_datetime().strftime("%Y%m%d")
        _log_path = Path(f"{_log_date}_{os.getpid()}.log")
        _handler = RotatingFileHandler(
            filename=_log_path,
            mode="a",  # text mode
            maxBytes=10 * 1024 * 1024,
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
            logger_factory=structlog.BytesLoggerFactory(
                file=BytesToTextIOWrapper(_handler)
            )
        )
        self._logger = structlog.get_logger()

    def get_logger(self) -> structlog.BoundLogger:
        """
        Returns:
            structlog.BoundLogger: The configured logger instance.
        """
        return self._logger
