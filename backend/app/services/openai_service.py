"""OpenAI service for making AI API calls with user API keys."""

import logging

from fastapi import HTTPException, status
from openai import APIConnectionError, APIError, OpenAI, RateLimitError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.models.user import User
from app.services.encryption_service import decrypt_api_key

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
        if not user.openai_api_key_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "API_KEY_NOT_CONFIGURED",
                    "message": ("Please configure your OpenAI API key " "in settings before using AI features"),
                },
            )

        try:
            # Decrypt user's API key
            decrypted_key = decrypt_api_key(user.openai_api_key_encrypted)

            # Initialize OpenAI client with user's key
            self.client = OpenAI(api_key=decrypted_key)
            self.user_id = user.id

        except Exception as e:
            logger.error(f"Failed to decrypt API key for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "API_KEY_DECRYPTION_FAILED",
                    "message": ("Failed to decrypt API key. Please " "reconfigure your API key."),
                },
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def _make_api_call(self, api_func, **kwargs):
        """Make an API call with retry logic.

        Args:
            api_func: OpenAI API function to call
            **kwargs: Arguments to pass to API function

        Returns:
            API response

        Raises:
            HTTPException: With user-friendly error message
        """
        try:
            return api_func(**kwargs)

        except RateLimitError:
            logger.warning(f"Rate limit hit for user {self.user_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "OPENAI_RATE_LIMIT",
                    "message": ("OpenAI rate limit exceeded. " "Please wait a moment and try again."),
                },
            ) from None

        except APIConnectionError as e:
            logger.error(f"OpenAI connection error for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "OPENAI_CONNECTION_ERROR",
                    "message": ("Unable to connect to OpenAI. Please check " "your internet connection and try again."),
                },
            ) from e

        except APIError as e:
            logger.error(f"OpenAI API error for user {self.user_id}: {str(e)}")

            # Check for authentication errors (invalid API key)
            if e.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_API_KEY",
                        "message": ("Your OpenAI API key is invalid. " "Please update it in settings."),
                    },
                ) from e

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "OPENAI_API_ERROR",
                    "message": f"OpenAI API error: {str(e)}",
                },
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error in OpenAI call for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "UNEXPECTED_ERROR",
                    "message": ("An unexpected error occurred. " "Please try again."),
                },
            ) from e

    def generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
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
        api_func = self.client.chat.completions.create

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = self._make_api_call(api_func, **kwargs)

        return response.choices[0].message.content
