"""Focused tests for OpenAI error classification and sanitization."""

from __future__ import annotations

from unittest.mock import Mock

import httpx
from openai import APIConnectionError, APIError
from openai import RateLimitError as OpenAIRateLimitError

from app.core.exceptions import (
    AuthenticationError,
    NetworkError,
    QuotaExceededError,
    ServerError,
)
from app.utils.error_handler import classify_openai_error, mask_secrets


def test_mask_secrets_masks_openai_style_keys():
    assert mask_secrets("sk-1234567890abcdef") == "***MASKED***"
    assert "***MASKED***" in mask_secrets("token=sk-1234567890abcdef")


def test_classify_connection_error_as_network_error():
    err = APIConnectionError(request=Mock())
    classified = classify_openai_error(err)
    assert isinstance(classified, NetworkError)


def test_classify_auth_error():
    api_err = APIError("Invalid", request=Mock(), body={"error": {"message": "Invalid"}})
    api_err.status_code = 401

    classified = classify_openai_error(api_err)
    assert isinstance(classified, AuthenticationError)


def test_classify_server_error():
    api_err = APIError("Boom", request=Mock(), body={"error": {"message": "Boom"}})
    api_err.status_code = 503

    classified = classify_openai_error(api_err)
    assert isinstance(classified, ServerError)


def test_classify_quota_exceeded_from_body_code():
    api_err = APIError(
        "Quota",
        request=Mock(),
        body={"error": {"message": "Quota", "code": "insufficient_quota"}},
    )
    api_err.status_code = 429

    classified = classify_openai_error(api_err)
    assert isinstance(classified, QuotaExceededError)


def test_classify_quota_exceeded_when_openai_raises_rate_limit_error():
    response = httpx.Response(
        429,
        request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
    )
    err = OpenAIRateLimitError(
        "Error code: 429 - insufficient_quota",
        response=response,
        body={
            "error": {
                "message": "You exceeded your current quota",
                "type": "insufficient_quota",
                "code": "insufficient_quota",
            }
        },
    )

    classified = classify_openai_error(err)
    assert isinstance(classified, QuotaExceededError)
