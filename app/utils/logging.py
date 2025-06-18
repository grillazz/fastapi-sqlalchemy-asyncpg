import logging

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

def setup_structlog() -> structlog.BoundLogger:
    log_date = Instant.now().py_datetime().strftime("%Y%m%d")
    log_path = Path(f"cuul_{log_date}_{os.getpid()}.log")
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
            file=log_path.open("wb")
        )
    )
    return structlog.get_logger()
