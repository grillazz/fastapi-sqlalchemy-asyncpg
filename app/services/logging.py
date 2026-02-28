import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import orjson
import structlog
from whenever._whenever import Instant

# ---------------------------------------------------------------------------
# Constants / defaults
# ---------------------------------------------------------------------------
_DEFAULT_LOG_PATH = "."
_DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MiB
_DEFAULT_BACKUP_COUNT = 5

# Generic registry: add any stdlib logger name + its desired level here.
_STDLIB_LOGGERS: dict[str, int] = {
    "root": logging.INFO,
    "uvicorn": logging.INFO,
    "sqlalchemy": logging.WARNING,
}

# Shared processor chain used by both structlog and the stdlib formatter.
_SHARED_PROCESSORS: list[structlog.types.Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.format_exc_info,
]


def _build_handler() -> RotatingFileHandler:
    log_dir = Path(os.getenv("ROTOGER_LOG_PATH", _DEFAULT_LOG_PATH))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{Instant.now().py_datetime().strftime('%Y%m%d')}_{os.getpid()}.log"

    handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=int(os.getenv("ROTOGER_LOG_MAX_BYTES", _DEFAULT_MAX_BYTES)),
        backupCount=int(os.getenv("ROTOGER_LOG_BACKUP_COUNT", _DEFAULT_BACKUP_COUNT)),
        encoding="utf-8",
    )
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=_SHARED_PROCESSORS,
            processor=structlog.processors.JSONRenderer(
                serializer=lambda *a, **kw: orjson.dumps(*a, **kw).decode()
            ),
        )
    )
    return handler


def _configure_logger() -> structlog.BoundLogger:
    """Configure structlog + stdlib loggers and return a bound logger."""
    structlog.configure(
        processors=[
            *_SHARED_PROCESSORS,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    handler = _build_handler()

    for name, level in _STDLIB_LOGGERS.items():
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.propagate = False
        logger.setLevel(level)

    return structlog.get_logger()


# Module-level singleton
_logger_instance = _configure_logger()


def get_logger() -> structlog.BoundLogger:
    """Return the configured singleton logger instance."""
    return _logger_instance
