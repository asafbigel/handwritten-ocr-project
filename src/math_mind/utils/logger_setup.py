import json
import logging
import sys
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects."""
    def format(self, record: logging.LogRecord) -> str:
        # We include the timestamp, log level, logger name, message, and source file/line.
        entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "file": f"{record.filename}:{record.lineno}", # We include the source file and line number for debugging purposes.
        }
        
        # If the log record includes exception info, we add it to the entry.
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)

        # We also include any extra fields passed in the log call, but we avoid overwriting reserved keys.
        builtin_keys = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "module", "msecs",
            "message", "msg", "name", "pathname", "process", "processName",
            "relativeCreated", "stack_info", "thread", "threadName", "taskName"
        }
        
        for key, value in record.__dict__.items():
            if key not in builtin_keys:
                entry[key] = value

        return json.dumps(entry, default=str)

def configure_logging(level: int = logging.INFO, log_file_path: str = "app.log") -> None:
    """Configures the root logger to output JSON to stderr and readable text to a file."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # 1. JSON formatter for console output
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(console_handler)

    # 2. Readable formatter for file output
    readable_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(readable_formatter)
    root_logger.addHandler(file_handler)

    # 3. Set log levels for third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)