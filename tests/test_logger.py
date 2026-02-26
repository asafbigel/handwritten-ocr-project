import json
import logging
import pytest
from io import StringIO

from math_mind.interfaces.logger import Logger
from math_mind.utils.standard_logger import (
    JsonFormatter,
    StandardLogger,
    StandardLoggerProvider,
)


@pytest.fixture(autouse=True)
def _clean_loggers():
    """Remove handlers added during tests so they don't leak between runs."""
    yield
    for name in list(logging.Logger.manager.loggerDict):
        if name.startswith("test_"):
            logging.getLogger(name).handlers.clear()


class TestJsonFormatter:
    def test_output_is_valid_json_with_expected_keys(self):
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_fmt", level=logging.INFO, pathname="", lineno=0,
            msg="hello", args=(), exc_info=None,
        )
        line = formatter.format(record)
        parsed = json.loads(line)
        assert parsed["level"] == "INFO"
        assert parsed["name"] == "test_fmt"
        assert parsed["message"] == "hello"
        assert "timestamp" in parsed

    def test_extra_fields_appear_in_output(self):
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_extra", level=logging.DEBUG, pathname="", lineno=0,
            msg="ctx", args=(), exc_info=None,
        )
        record.extra_fields = {"x": 10, "region": "top"}
        line = formatter.format(record)
        parsed = json.loads(line)
        assert parsed["x"] == 10
        assert parsed["region"] == "top"


class TestStandardLogger:
    @pytest.fixture
    def captured_logger(self):
        stream = StringIO()
        stdlib_logger = logging.getLogger("test_standard_logger")
        stdlib_logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        stdlib_logger.addHandler(handler)
        return StandardLogger(stdlib_logger), stream

    @pytest.mark.parametrize("method,level", [
        ("debug", "DEBUG"),
        ("info", "INFO"),
        ("warning", "WARNING"),
        ("error", "ERROR"),
        ("critical", "CRITICAL"),
    ])
    def test_log_methods_write_json_with_correct_level(self, captured_logger, method, level):
        logger, stream = captured_logger
        getattr(logger, method)("test message")
        parsed = json.loads(stream.getvalue().strip())
        assert parsed["level"] == level
        assert parsed["message"] == "test message"

    def test_kwargs_appear_as_extra_fields(self, captured_logger):
        logger, stream = captured_logger
        logger.info("masked", x_start=5, y_end=20)
        parsed = json.loads(stream.getvalue().strip())
        assert parsed["x_start"] == 5
        assert parsed["y_end"] == 20


class TestStandardLoggerProvider:
    def test_get_logger_returns_standard_logger(self):
        provider = StandardLoggerProvider()
        logger = provider.get_logger("test_provider_ret")
        assert isinstance(logger, StandardLogger)
        assert isinstance(logger, Logger)

    def test_same_name_returns_same_instance(self):
        provider = StandardLoggerProvider()
        a = provider.get_logger("test_provider_same")
        b = provider.get_logger("test_provider_same")
        assert a is b

    def test_no_duplicate_handlers(self):
        provider = StandardLoggerProvider()
        provider.get_logger("test_provider_dup")
        provider.get_logger("test_provider_dup")
        stdlib_logger = logging.getLogger("test_provider_dup")
        assert len(stdlib_logger.handlers) == 1
