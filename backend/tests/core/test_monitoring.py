"""Tests for lightweight monitoring/metrics utilities."""

from app.core.monitoring import (
    get_openai_error_counts,
    record_openai_error,
    reset_openai_error_counts,
)


def test_record_openai_error_increments_counts():
    reset_openai_error_counts()

    record_openai_error(category="network", error_code="OPENAI_CONNECTION_ERROR")
    record_openai_error(category="network", error_code="OPENAI_CONNECTION_ERROR")
    record_openai_error(category="rate_limit", error_code="OPENAI_RATE_LIMIT")

    counts = get_openai_error_counts()

    assert counts["by_category"]["network"] == 2
    assert counts["by_category"]["rate_limit"] == 1
    assert counts["by_error_code"]["OPENAI_CONNECTION_ERROR"] == 2
    assert counts["by_error_code"]["OPENAI_RATE_LIMIT"] == 1
