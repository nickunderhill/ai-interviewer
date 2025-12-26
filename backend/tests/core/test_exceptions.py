"""Tests for custom OpenAI integration exceptions."""

import pytest

from app.core.exceptions import (
    AuthenticationError,
    InvalidResponseError,
    NetworkError,
    OpenAIIntegrationError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
)


@pytest.mark.parametrize(
    "exc_cls,code",
    [
        (NetworkError, "NETWORK_ERROR"),
        (AuthenticationError, "INVALID_API_KEY"),
        (RateLimitError, "RATE_LIMIT"),
        (ServerError, "SERVER_ERROR"),
        (InvalidResponseError, "INVALID_RESPONSE"),
        (QuotaExceededError, "QUOTA_EXCEEDED"),
    ],
)
def test_openai_exceptions_have_error_code_and_message(exc_cls, code):
    err = exc_cls("hello", error_code=code)

    assert isinstance(err, OpenAIIntegrationError)
    assert err.message == "hello"
    assert err.error_code == code
    assert str(err) == "hello"


def test_openai_exception_can_store_original_error_and_details():
    original = ValueError("boom")
    err = NetworkError(
        "network down",
        error_code="NETWORK_ERROR",
        original_error=original,
        details={"operation_type": "question_generation"},
    )

    assert err.original_error is original
    assert err.details == {"operation_type": "question_generation"}
