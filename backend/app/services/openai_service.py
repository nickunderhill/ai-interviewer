"""OpenAI service for making AI API calls with user API keys.

This layer:
- Decrypts user API keys
- Classifies OpenAI SDK errors into app-specific error categories
- Retries only transient failures with exponential backoff
- Raises FastAPI HTTPException with user-friendly messages (never secrets)
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, status
from openai import AsyncOpenAI

from app.core.exceptions import (
    AuthenticationError,
    InvalidResponseError,
    NetworkError,
    OpenAIIntegrationError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
)
from app.core.monitoring import record_openai_error, report_to_monitoring_service
from app.models.user import User
from app.services.encryption_service import decrypt_api_key
from app.utils.error_handler import classify_openai_error, mask_secrets
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for making OpenAI API calls with user's API key.

    Handles API key decryption, retry logic, and error handling.
    """

    def __init__(self, user: User):
        """Initialize OpenAI service with user's encrypted API key.

        Args:
            user: User object containing encrypted OpenAI API key

        Raises:
            HTTPException: If user hasn't configured API key or
                          decryption fails
        """
        encrypted_api_key = getattr(user, "encrypted_api_key", None)
        if encrypted_api_key is None:
            # Backward-compatible fallback for older attribute name.
            encrypted_api_key = getattr(user, "openai_api_key_encrypted", None)

        if not encrypted_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "API_KEY_NOT_CONFIGURED",
                    "message": ("Please configure your OpenAI API key " "in settings before using AI features"),
                },
            )

        try:
            # Decrypt user's API key
            decrypted_key = decrypt_api_key(encrypted_api_key)

            # Initialize OpenAI client with user's key
            self.client = AsyncOpenAI(api_key=decrypted_key)
            self.user_id = user.id

        except Exception as e:
            logger.error(
                "Failed to decrypt API key",
                extra={"user_id": str(user.id), "error_type": type(e).__name__},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "API_KEY_DECRYPTION_FAILED",
                    "message": ("Failed to decrypt API key. Please " "reconfigure your API key."),
                },
            ) from e

    @async_retry(
        max_retries=3,
        backoff_base_seconds=1.0,
        retriable_exceptions=(NetworkError, ServerError),
        jitter_ratio=0.1,
        log_context_provider=lambda args, kwargs: {
            **(kwargs.get("context") or {}),
            "user_id": str(getattr(args[0], "user_id", "")),
        },
    )
    async def _chat_completion_create(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None,
        context: dict[str, Any] | None,
    ):
        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            return await self.client.chat.completions.create(**kwargs)
        except Exception as e:
            raise classify_openai_error(e) from e

    async def generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
        *,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Generate a chat completion using OpenAI.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: OpenAI model to use (default: gpt-3.5-turbo)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text content

        Raises:
            HTTPException: If API call fails
        """
        try:
            logger.info(
                "OpenAI call started",
                extra={
                    **(context or {}),
                    "user_id": str(self.user_id),
                    "model": model,
                },
            )

            response = await self._chat_completion_create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                context=context,
            )

            content = None
            try:
                content = response.choices[0].message.content
            except Exception:
                content = None

            if not content:
                raise InvalidResponseError(
                    message="OpenAI returned an empty response.",
                    error_code="EMPTY_RESPONSE",
                )

            usage = getattr(response, "usage", None)
            tokens_used = getattr(usage, "total_tokens", 0) if usage is not None else 0

            logger.info(
                "OpenAI call completed",
                extra={
                    **(context or {}),
                    "user_id": str(self.user_id),
                    "model": model,
                    "tokens_used": tokens_used,
                },
            )

            return content

        except OpenAIIntegrationError as e:
            safe_message = mask_secrets(e.message)
            log_extra = {
                **(context or {}),
                "user_id": str(self.user_id),
                "error_code": e.error_code,
                "error_type": type(e).__name__,
            }

            if isinstance(e, AuthenticationError):
                category = "authentication"
            elif isinstance(e, QuotaExceededError):
                category = "quota"
            elif isinstance(e, RateLimitError):
                category = "rate_limit"
            elif isinstance(e, NetworkError):
                category = "network"
            elif isinstance(e, ServerError):
                category = "server"
            else:
                category = "invalid_response"

            record_openai_error(category=category, error_code=e.error_code)

            # Logging levels: transient WARNING, others ERROR
            if isinstance(e, NetworkError | ServerError | RateLimitError):
                logger.warning("OpenAI call failed", extra=log_extra, exc_info=True)
            else:
                logger.error("OpenAI call failed", extra=log_extra, exc_info=True)

            if isinstance(e, AuthenticationError | QuotaExceededError):
                report_to_monitoring_service(
                    event="openai_critical_error",
                    payload={
                        **log_extra,
                        "category": category,
                        "message": safe_message,
                    },
                )

            if isinstance(e, AuthenticationError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "INVALID_API_KEY", "message": safe_message},
                ) from e

            if isinstance(e, RateLimitError):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={"code": "OPENAI_RATE_LIMIT", "message": safe_message},
                ) from e

            if isinstance(e, QuotaExceededError):
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={"code": "OPENAI_QUOTA_EXCEEDED", "message": safe_message},
                ) from e

            if isinstance(e, NetworkError):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={"code": "OPENAI_CONNECTION_ERROR", "message": safe_message},
                ) from e

            if isinstance(e, ServerError):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={"code": "OPENAI_SERVER_ERROR", "message": safe_message},
                ) from e

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"code": "OPENAI_INVALID_RESPONSE", "message": safe_message},
            ) from e

        except Exception as e:
            safe_message = mask_secrets(str(e))
            record_openai_error(category="unexpected", error_code="UNEXPECTED_ERROR")
            logger.error(
                "Unexpected OpenAI integration error",
                extra={"user_id": str(self.user_id), **(context or {})},
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "UNEXPECTED_ERROR", "message": safe_message},
            ) from e
