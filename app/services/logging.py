import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import orjson
import structlog
from whenever._whenever import Instant


def _configure_logger() -> structlog.BoundLogger:
    """
    Configures and returns a structlog logger with a rotating file handler.

    The logger is configured using environment variables for path, file size,
    and backup count. It formats logs as JSON.
    """
    log_dir = Path(os.environ.get("ROTOGER_LOG_PATH", "."))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_date = Instant.now().py_datetime().strftime("%Y%m%d")
    log_path = log_dir / f"{log_date}_{os.getpid()}.log"

    # Use int() to ensure env var values are correctly typed
    max_bytes = int(os.environ.get("ROTOGER_LOG_MAX_BYTES", 10 * 1024 * 1024))
    backup_count = int(os.environ.get("ROTOGER_LOG_BACKUP_COUNT", 5))

    handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",

    )

    # Use structlog's standard library integration
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            # structlog.stdlib.add_logger_name,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the underlying standard logger
    formatter = structlog.stdlib.ProcessorFormatter(
        # These run after the processors defined in structlog.configure
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.format_exc_info,
            structlog.stdlib.add_logger_name,
        ],
        processor=structlog.processors.JSONRenderer(
            serializer=lambda *args, **kwargs: orjson.dumps(*args, **kwargs).decode()
        ),
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger("root")  # Get the root logger
    root_logger.addHandler(handler)
    root_logger.propagate = False  # Prevent logs from being propagated to the root logger
    root_logger.setLevel(logging.INFO)

    uvicorn_logger = logging.getLogger("uvicorn")  # Get the root logger
    uvicorn_logger.addHandler(handler)
    uvicorn_logger.propagate = False  # Prevent logs from being propagated to the root logger
    uvicorn_logger.setLevel(logging.INFO)

    sa_logger = logging.getLogger("sqlalchemy")  # Get the root logger
    sa_logger.addHandler(handler)
    sa_logger.propagate = False  # Prevent logs from being propagated to the root logger
    sa_logger.setLevel(logging.WARNING)

    # Set SQLAlchemy engine logger level specifically if needed
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    return structlog.get_logger()



# Module-level singleton instance
_logger_instance = _configure_logger()


def get_logger() -> structlog.BoundLogger:
    """
    Returns the configured singleton logger instance.
    """
    return _logger_instance
