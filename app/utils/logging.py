from logging.handlers import RotatingFileHandler

from rich.console import Console
from rich.logging import RichHandler

from app.utils.singleton import SingletonMeta

import logging
import os
import orjson
import structlog
from whenever._whenever import Instant
from pathlib import Path

class AppLogger(metaclass=SingletonMeta):
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def get_logger(self):
        return self._logger


class RichConsoleHandler(RichHandler):
    def __init__(self, width=200, style=None, **kwargs):
        super().__init__(
            console=Console(color_system="256", width=width, style=style, stderr=True),
            **kwargs,
        )


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


def setup_structlog() -> structlog.BoundLogger:
    log_date = Instant.now().py_datetime().strftime("%Y%m%d")
    log_path = Path(f"{log_date}_{os.getpid()}.log")
    handler = RotatingFileHandler(
        filename=log_path,
        mode="a",  # text mode
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_like = BytesToTextIOWrapper(handler)
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
            file=file_like
        )
    )
    return structlog.get_logger()
