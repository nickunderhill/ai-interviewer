"""Lightweight monitoring hooks and in-process metrics.

This module intentionally avoids external dependencies (e.g. Prometheus/Sentry)
while providing a single place to increment counters and integrate future
monitoring backends.
"""

from __future__ import annotations

from collections import Counter
from threading import Lock
from typing import Any

_openai_error_by_category: Counter[str] = Counter()
_openai_error_by_code: Counter[str] = Counter()
_lock = Lock()


def record_openai_error(*, category: str, error_code: str) -> None:
    """Increment OpenAI error counters.

    Args:
        category: High-level category (e.g. 'network', 'rate_limit', 'quota')
        error_code: Stable code used in API responses/logging
    """
    with _lock:
        _openai_error_by_category[category] += 1
        _openai_error_by_code[error_code] += 1


def get_openai_error_counts() -> dict[str, dict[str, int]]:
    """Return a snapshot of current OpenAI error counters."""
    with _lock:
        return {
            "by_category": dict(_openai_error_by_category),
            "by_error_code": dict(_openai_error_by_code),
        }


def reset_openai_error_counts() -> None:
    """Reset OpenAI error counters (useful for tests)."""
    with _lock:
        _openai_error_by_category.clear()
        _openai_error_by_code.clear()


def report_to_monitoring_service(*, event: str, payload: dict[str, Any]) -> None:
    """Placeholder hook for external monitoring integrations.

    Intentionally a no-op today. Wire this to Sentry/Datadog/etc later.
    """
    _ = (event, payload)
