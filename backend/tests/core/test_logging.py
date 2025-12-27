"""Tests for JSON logging configuration and sensitive data scrubbing."""

from __future__ import annotations

from io import StringIO
import json
import logging

import pytest

from app.core.logging_config import JSONFormatter, configure_logging


class TestJSONFormatter:
    """Tests for JSON log formatter."""

    def test_basic_log_format(self):
        """Test that log record is formatted as valid JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        log_data = json.loads(output)

        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test message"
        assert "timestamp" in log_data

    def test_sensitive_field_masking_in_extra(self):
        """Test that sensitive fields in extra dict are masked."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Auth attempt",
            args=(),
            exc_info=None,
        )
        record.password = "secret123"
        record.api_key = "sk-1234567890"
        record.user_id = 42

        output = formatter.format(record)
        log_data = json.loads(output)

        assert log_data["password"] == "***MASKED***"
        assert log_data["api_key"] == "***MASKED***"
        assert log_data["user_id"] == 42

    def test_sensitive_keyword_in_field_name(self):
        """Test that fields with sensitive keywords in their names are masked."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test",
            args=(),
            exc_info=None,
        )
        record.user_token = "abc123"
        record.secret_value = "confidential"
        record.authorization_header = "Bearer xyz"

        output = formatter.format(record)
        log_data = json.loads(output)

        assert log_data["user_token"] == "***MASKED***"
        assert log_data["secret_value"] == "***MASKED***"
        assert log_data["authorization_header"] == "***MASKED***"

    def test_message_masking_with_mask_secrets(self):
        """Test that message content is masked using mask_secrets function."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="API key: sk-1234567890abcdef",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        log_data = json.loads(output)

        # mask_secrets should replace sk-* patterns
        assert "sk-1234567890abcdef" not in log_data["message"]
        assert "***MASKED***" in log_data["message"]

    def test_exception_info_included(self):
        """Test that exception info is included in output."""
        formatter = JSONFormatter()
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        output = formatter.format(record)
        log_data = json.loads(output)

        assert "exception" in log_data
        assert "ValueError: Test error" in log_data["exception"]
        assert "Traceback" in log_data["exception"]

    def test_reserved_fields_not_included(self):
        """Test that reserved LogRecord fields are not duplicated."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        log_data = json.loads(output)

        # These should not appear in output
        assert "pathname" not in log_data
        assert "lineno" not in log_data
        assert "funcName" not in log_data


class TestConfigureLogging:
    """Tests for logging configuration."""

    @pytest.fixture
    def capture_logs(self):
        """Fixture to capture log output."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)

        # Clear any existing handlers
        root = logging.getLogger()
        original_handlers = root.handlers.copy()
        root.handlers.clear()
        root.addHandler(handler)

        yield stream

        # Restore original handlers
        root.handlers.clear()
        for h in original_handlers:
            root.addHandler(h)

    def test_configure_logging_sets_json_formatter(self, capture_logs):
        """Test that configure_logging sets up JSON formatter."""
        configure_logging(logging.INFO)

        logger = logging.getLogger("test")
        logger.info("Test message")

        output = capture_logs.getvalue()
        log_data = json.loads(output.strip())

        assert log_data["message"] == "Test message"
        assert log_data["level"] == "INFO"

    def test_configure_logging_is_idempotent(self, capture_logs):
        """Test that calling configure_logging multiple times is safe."""
        configure_logging(logging.INFO)
        configure_logging(logging.DEBUG)

        logger = logging.getLogger("test")
        logger.info("Test message")

        output = capture_logs.getvalue()
        lines = output.strip().split("\n")

        # Should only have one log line, not duplicates
        assert len(lines) == 1

    def test_configure_logging_respects_level(self, capture_logs):
        """Test that logging level is properly set."""
        configure_logging(logging.WARNING)

        logger = logging.getLogger("test")
        logger.info("Info message")
        logger.warning("Warning message")

        output = capture_logs.getvalue()

        # Only warning should be logged
        assert "Info message" not in output
        assert "Warning message" in output


class TestSensitiveDataScrubbing:
    """Integration tests for sensitive data scrubbing."""

    def test_nested_dict_scrubbing(self):
        """Test scrubbing in extra dict with structured data."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Request",
            args=(),
            exc_info=None,
        )
        # If field name contains sensitive keyword, it's masked
        record.api_key = "sk-actual-key"
        record.request_data = "contains some data"
        record.normal_field = "safe_value"

        output = formatter.format(record)
        log_data = json.loads(output)

        # Field with sensitive keyword should be masked
        assert log_data["api_key"] == "***MASKED***"
        # String values are passed through mask_secrets which masks sk-* patterns
        assert log_data["request_data"] == "contains some data"
        assert log_data["normal_field"] == "safe_value"

    def test_multiple_sensitive_patterns(self):
        """Test message with multiple sensitive patterns."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Keys: sk-abc123def456 and sk-xyz789ghi012",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        log_data = json.loads(output)

        # Both API keys should be masked
        assert "sk-abc123def456" not in log_data["message"]
        assert "sk-xyz789ghi012" not in log_data["message"]
        assert log_data["message"].count("***MASKED***") == 2
