# Story 8.1: Implement Comprehensive OpenAI Integration Error Handling

Status: ready-for-dev

## Story

As a developer, I want to implement robust error handling for OpenAI API calls,
so that the system gracefully handles all failure scenarios.

## Acceptance Criteria

1. **Given** I'm implementing OpenAI integration **When** any OpenAI API call
   fails **Then** the system catches and handles: network errors (connection
   timeout, DNS failure), authentication errors (401 invalid API key), rate
   limiting (429), server errors (5xx), invalid response format, quota exceeded
   errors **And** implements exponential backoff retry for transient errors
   (network, 5xx) with max 3 retries **And** logs all errors with context
   (operation type, session id, error details) without exposing API keys **And**
   returns user-friendly error messages **And** updates Operation status to
   'failed' with error_message **And** never crashes or leaves operations in
   inconsistent state (NFR19, NFR20) ✅

## Tasks / Subtasks

- [ ] Task 1: Create comprehensive error classification system (AC: #1)

  - [ ] Define error categories: NetworkError, AuthenticationError,
        RateLimitError, ServerError, InvalidResponseError, QuotaExceededError
  - [ ] Create custom exception classes in `backend/app/core/exceptions.py`
  - [ ] Add error_code field to each exception for structured logging

- [ ] Task 2: Implement retry logic with exponential backoff (AC: #1)

  - [ ] Create retry decorator in `backend/app/utils/retry.py`
  - [ ] Configure retry for transient errors only (network, 5xx)
  - [ ] Implement exponential backoff: 1s, 2s, 4s (max 3 retries)
  - [ ] Add jitter to prevent thundering herd
  - [ ] Log each retry attempt with context

- [ ] Task 3: Update OpenAI service with comprehensive error handling (AC: #1)

  - [ ] Wrap all OpenAI API calls in try/except blocks
  - [ ] Classify errors into appropriate categories
  - [ ] Apply retry decorator to transient error types
  - [ ] Update Operation model status to 'failed' on unrecoverable errors
  - [ ] Store error_message in Operation model
  - [ ] Never expose API keys in logs or error messages

- [ ] Task 4: Implement structured error logging (AC: #1)

  - [ ] Log all errors with structured context (JSON format)
  - [ ] Include: timestamp, operation_id, session_id, error_type, error_message
  - [ ] Mask sensitive data (API keys, user PII) in logs
  - [ ] Use Python logging module with appropriate levels
  - [ ] Add stack traces for unexpected errors

- [ ] Task 5: Create error recovery mechanisms (AC: #1)

  - [ ] Ensure database transactions are rolled back on errors
  - [ ] Mark Operation as 'failed' atomically
  - [ ] Clean up any partial state (e.g., incomplete message records)
  - [ ] Prevent resource leaks (connections, file handles)

- [ ] Task 6: Add error monitoring and alerting hooks (AC: #1)
  - [ ] Log critical errors (authentication, quota) at ERROR level
  - [ ] Log transient errors at WARNING level
  - [ ] Add metrics for error rates by category
  - [ ] Prepare hooks for external monitoring services

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Error Classification:** All OpenAI errors categorized and handled
  consistently
- **Retry Strategy:** Exponential backoff for transient errors only
- **Logging:** Structured JSON logging with sensitive data masking
- **Transactions:** Atomic operations with proper rollback
- **Operation Model:** Status updates are atomic and consistent

**Technology Stack:**

- Python 3.11+ with async/await patterns
- SQLAlchemy 2.0+ async for database operations
- Python `logging` module with JSON formatter
- Custom retry decorator using `asyncio.sleep()`

### File Structure

```
backend/app/
├── core/
│   ├── exceptions.py          # Custom exception classes
│   └── logging_config.py      # Structured logging configuration
├── utils/
│   ├── retry.py               # Retry decorator with exponential backoff
│   └── error_handler.py       # Error classification and handling utilities
├── services/
│   └── openai_service.py      # Update with comprehensive error handling
└── models/
    └── operation.py           # Ensure Operation model supports error_message field
```

### Implementation Details

**Custom Exception Classes:**

```python
# backend/app/core/exceptions.py
class OpenAIError(Exception):
    """Base exception for OpenAI integration errors."""
    def __init__(self, message: str, error_code: str, original_error: Exception = None):
        self.message = message
        self.error_code = error_code
        self.original_error = original_error
        super().__init__(message)

class NetworkError(OpenAIError):
    """Network-related errors (connection timeout, DNS failure)."""
    pass

class AuthenticationError(OpenAIError):
    """Authentication errors (401, invalid API key)."""
    pass

class RateLimitError(OpenAIError):
    """Rate limiting errors (429)."""
    pass

class ServerError(OpenAIError):
    """Server errors (5xx)."""
    pass

class InvalidResponseError(OpenAIError):
    """Invalid or unexpected response format."""
    pass

class QuotaExceededError(OpenAIError):
    """Quota exceeded errors."""
    pass
```

**Retry Decorator:**

```python
# backend/app/utils/retry.py
import asyncio
import random
from functools import wraps
from typing import Type, Tuple
import logging

logger = logging.getLogger(__name__)

def async_retry(
    max_retries: int = 3,
    backoff_base: float = 1.0,
    retriable_exceptions: Tuple[Type[Exception], ...] = (NetworkError, ServerError),
):
    """
    Decorator for async functions with exponential backoff retry.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_base: Base delay in seconds (default: 1.0)
        retriable_exceptions: Tuple of exception types that should trigger retry
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retriable_exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        delay = backoff_base * (2 ** attempt)
                        jitter = random.uniform(0, 0.1 * delay)
                        wait_time = delay + jitter

                        logger.warning(
                            f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__}",
                            extra={
                                "function": func.__name__,
                                "attempt": attempt + 1,
                                "max_retries": max_retries,
                                "wait_time": wait_time,
                                "error": str(e),
                            }
                        )

                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {max_retries} retries exhausted for {func.__name__}",
                            extra={
                                "function": func.__name__,
                                "error": str(e),
                            }
                        )
                except Exception as e:
                    # Non-retriable exceptions are raised immediately
                    logger.error(
                        f"Non-retriable error in {func.__name__}: {e}",
                        extra={"function": func.__name__, "error": str(e)}
                    )
                    raise

            # Raise the last exception after all retries exhausted
            if last_exception:
                raise last_exception

        return wrapper
    return decorator
```

**Updated OpenAI Service:**

```python
# backend/app/services/openai_service.py (excerpt)
import logging
from openai import AsyncOpenAI, APIError, RateLimitError as OpenAIRateLimitError
from app.core.exceptions import (
    NetworkError, AuthenticationError, RateLimitError,
    ServerError, InvalidResponseError, QuotaExceededError
)
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    def _classify_openai_error(self, error: Exception) -> OpenAIError:
        """Classify OpenAI errors into custom exception types."""
        error_str = str(error)

        if isinstance(error, OpenAIRateLimitError) or "429" in error_str:
            return RateLimitError(
                "OpenAI rate limit exceeded. Please wait before retrying.",
                "RATE_LIMIT_EXCEEDED",
                error
            )

        if "401" in error_str or "invalid api key" in error_str.lower():
            return AuthenticationError(
                "Invalid OpenAI API key. Please check your configuration.",
                "INVALID_API_KEY",
                error
            )

        if "insufficient_quota" in error_str or "quota" in error_str.lower():
            return QuotaExceededError(
                "OpenAI quota exceeded. Please check your account.",
                "QUOTA_EXCEEDED",
                error
            )

        if "timeout" in error_str.lower() or "connection" in error_str.lower():
            return NetworkError(
                "Network error connecting to OpenAI. Please try again.",
                "NETWORK_ERROR",
                error
            )

        if "500" in error_str or "502" in error_str or "503" in error_str:
            return ServerError(
                "OpenAI service temporarily unavailable. Retrying...",
                "SERVER_ERROR",
                error
            )

        return InvalidResponseError(
            "Unexpected error from OpenAI API.",
            "INVALID_RESPONSE",
            error
        )

    @async_retry(max_retries=3, backoff_base=1.0, retriable_exceptions=(NetworkError, ServerError))
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """
        Generate completion with comprehensive error handling and retry logic.
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

            if not response.choices or not response.choices[0].message.content:
                raise InvalidResponseError(
                    "OpenAI returned empty response",
                    "EMPTY_RESPONSE"
                )

            return response.choices[0].message.content

        except Exception as e:
            # Classify and re-raise as custom exception
            classified_error = self._classify_openai_error(e)

            logger.error(
                "OpenAI API error",
                extra={
                    "error_code": classified_error.error_code,
                    "error_message": classified_error.message,
                    "operation": "generate_completion",
                },
                exc_info=True
            )

            raise classified_error
```

**Structured Logging Configuration:**

```python
# backend/app/core/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format log records as JSON with sensitive data masking."""

    SENSITIVE_KEYS = ['api_key', 'password', 'token', 'secret']

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, 'extra'):
            extra = record.extra
            # Mask sensitive data
            for key, value in extra.items():
                if any(sensitive in key.lower() for sensitive in self.SENSITIVE_KEYS):
                    log_data[key] = '***MASKED***'
                else:
                    log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def configure_logging():
    """Configure structured logging for the application."""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
```

### Testing Requirements

**Test Coverage:**

- All error types are properly classified
- Retry logic works with exponential backoff
- Non-retriable errors are not retried
- Error messages are user-friendly and don't expose API keys
- Operation status is updated correctly on failure
- Structured logging captures all required context

**Test Files:**

- `backend/tests/services/test_openai_error_handling.py`
- `backend/tests/utils/test_retry.py`
- `backend/tests/core/test_exceptions.py`

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.1]
- [Source: _bmad-output/architecture.md#Error-Handling-Patterns]
- [Source: _bmad-output/project-context.md#Backend-Patterns]
- [NFR19: Graceful Error Handling]
- [NFR20: Zero Data Loss]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with comprehensive error handling patterns
- Ready for dev implementation
- All error types classified and documented
- Retry logic with exponential backoff specified
- Structured logging configuration provided
