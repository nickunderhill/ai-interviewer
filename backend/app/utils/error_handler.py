"""Utilities for classifying and sanitizing OpenAI-related errors."""

from __future__ import annotations

import re
from typing import Any

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
)
from openai import (
    RateLimitError as OpenAIRateLimitError,
)

from app.core.exceptions import (
    AuthenticationError,
    InvalidResponseError,
    NetworkError,
    OpenAIIntegrationError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
)

_API_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9]{10,}\b")


def mask_secrets(text: str) -> str:
    """Mask common secret patterns (best-effort)."""
    return _API_KEY_RE.sub("***MASKED***", text)


def _extract_status_code(error: Exception) -> int | None:
    return getattr(error, "status_code", None)


def _extract_body(error: Exception) -> Any:
    return getattr(error, "body", None)


def classify_openai_error(error: Exception) -> OpenAIIntegrationError:
    """Classify OpenAI SDK exceptions into app-specific error types."""

    if isinstance(error, APIConnectionError | APITimeoutError):
        return NetworkError(
            message="Network error connecting to OpenAI. Please try again.",
            error_code="NETWORK_ERROR",
            original_error=error,
        )

    if isinstance(error, OpenAIRateLimitError):
        return RateLimitError(
            message="OpenAI rate limit exceeded. Please wait and try again.",
            error_code="RATE_LIMIT",
            original_error=error,
        )

    if isinstance(error, APIError):
        status_code = _extract_status_code(error)
        body = _extract_body(error)

        # Authentication
        if status_code == 401:
            return AuthenticationError(
                message="Invalid OpenAI API key. Please update it in settings.",
                error_code="INVALID_API_KEY",
                original_error=error,
            )

        # Quota / billing
        # OpenAI commonly returns code: "insufficient_quota"
        code = None
        try:
            code = (body or {}).get("error", {}).get("code")
        except Exception:
            code = None

        if code == "insufficient_quota" or "quota" in str(error).lower():
            return QuotaExceededError(
                message="OpenAI quota exceeded. Please check your plan/billing.",
                error_code="QUOTA_EXCEEDED",
                original_error=error,
            )

        # Rate limit (429)
        if status_code == 429:
            return RateLimitError(
                message="OpenAI rate limit exceeded. Please wait and try again.",
                error_code="RATE_LIMIT",
                original_error=error,
            )

        # Server 5xx
        if status_code is not None and 500 <= status_code <= 599:
            return ServerError(
                message="OpenAI service temporarily unavailable.",
                error_code="SERVER_ERROR",
                original_error=error,
            )

        # Fallback
        return InvalidResponseError(
            message="Unexpected response from OpenAI.",
            error_code="INVALID_RESPONSE",
            original_error=error,
        )

    # Unknown
    return InvalidResponseError(
        message="Unexpected error from OpenAI.",
        error_code="INVALID_RESPONSE",
        original_error=error,
    )
