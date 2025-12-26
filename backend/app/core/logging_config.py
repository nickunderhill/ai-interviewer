"""Structured JSON logging configuration.

Keeps logs machine-readable and masks common sensitive values.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.utils.error_handler import mask_secrets


_RESERVED_LOG_RECORD_KEYS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""

    SENSITIVE_KEYWORDS = ("api_key", "password", "token", "secret", "authorization")

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": mask_secrets(record.getMessage()),
        }

        # Include extra fields added via logger.*(extra={...})
        for key, value in record.__dict__.items():
            if key in _RESERVED_LOG_RECORD_KEYS:
                continue

            if any(k in key.lower() for k in self.SENSITIVE_KEYWORDS):
                payload[key] = "***MASKED***"
                continue

            if isinstance(value, str):
                payload[key] = mask_secrets(value)
            else:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging to JSON format.

    Idempotent: if handlers already exist, replaces their formatters.
    """

    root = logging.getLogger()
    root.setLevel(level)

    formatter = JSONFormatter()

    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root.addHandler(handler)
        return

    for handler in root.handlers:
        handler.setFormatter(formatter)
