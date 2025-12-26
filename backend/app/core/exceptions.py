"""Custom exception types for OpenAI integration.

These exceptions are intended for internal classification and structured logging.
Public API responses should be produced by converting these to HTTPException with
safe, user-friendly messages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OpenAIIntegrationError(Exception):
    """Base exception for OpenAI integration failures."""

    message: str
    error_code: str
    original_error: Exception | None = None
    details: dict[str, Any] | None = None

    def __str__(self) -> str:  # pragma: no cover
        return self.message


class NetworkError(OpenAIIntegrationError):
    """Network-related errors (connection timeout, DNS failure)."""


class AuthenticationError(OpenAIIntegrationError):
    """Authentication errors (401 invalid API key)."""


class RateLimitError(OpenAIIntegrationError):
    """Rate limiting errors (429)."""


class ServerError(OpenAIIntegrationError):
    """Server errors (5xx)."""


class InvalidResponseError(OpenAIIntegrationError):
    """Invalid or unexpected response format."""


class QuotaExceededError(OpenAIIntegrationError):
    """Quota exceeded or billing-related errors."""
