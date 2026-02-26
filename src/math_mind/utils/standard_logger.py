import json
import logging
import sys
from datetime import datetime, timezone

from math_mind.interfaces.logger import Logger, LoggerProvider


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if extra:
            entry.update(extra)
        return json.dumps(entry, default=str)


class StandardLogger(Logger):
    """Logger implementation backed by Python's stdlib logging with JSON output."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def _log(self, level: int, message: str, **kwargs) -> None:
        self._logger.log(level, message, extra={"extra_fields": kwargs})

    def debug(self, message: str, **kwargs) -> None:
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self._log(logging.CRITICAL, message, **kwargs)


class StandardLoggerProvider(LoggerProvider):
    """Creates StandardLogger instances writing JSON to stderr."""

    def __init__(self, level: int = logging.INFO) -> None:
        self._level = level
        self._loggers: dict[str, StandardLogger] = {}

    def get_logger(self, name: str) -> StandardLogger:
        if name in self._loggers:
            return self._loggers[name]

        stdlib_logger = logging.getLogger(name)
        stdlib_logger.setLevel(self._level)

        if not stdlib_logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(JsonFormatter())
            stdlib_logger.addHandler(handler)

        wrapped = StandardLogger(stdlib_logger)
        self._loggers[name] = wrapped
        return wrapped
