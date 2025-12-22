# Story 4.6: Implement OpenAI Service for API Calls

Status: ready-for-dev

## Story

As a developer, I want to create a service layer for OpenAI API calls, so that
we have centralized error handling and retry logic for AI operations.

## Acceptance Criteria

1. **Given** I'm implementing AI integration **When** I create the OpenAI
   service class **Then** it loads the API key from encrypted user storage
   (using Fernet decryption) **And** implements retry logic with exponential
   backoff for transient failures **And** handles rate limiting (429) and server
   errors (5xx) gracefully **And** never logs or exposes the raw API key **And**
   returns structured responses or raises specific exceptions **And** uses the
   user's configured OpenAI API key (not a system-wide key)

## Tasks / Subtasks

- [ ] Task 1: Create OpenAI service class structure (AC: #1)

  - [ ] Create `backend/app/services/openai_service.py` with OpenAIService class
  - [ ] Accept user object in constructor to load encrypted API key
  - [ ] Decrypt API key using encryption service from story 2.9
  - [ ] Initialize OpenAI client with user's decrypted API key
  - [ ] Validate API key is configured (raise error if user hasn't set key)

- [ ] Task 2: Implement retry logic with exponential backoff (AC: #1)

  - [ ] Use tenacity library for retry logic
  - [ ] Configure max 3 retries with exponential backoff (1s, 2s, 4s)
  - [ ] Retry on transient errors: rate limit (429), server errors (500-503)
  - [ ] Don't retry on client errors (400, 401, 403) or permanent failures
  - [ ] Log retry attempts (without exposing API key)

- [ ] Task 3: Implement base API call method (AC: #1)

  - [ ] Create \_make_api_call method with error handling
  - [ ] Wrap OpenAI API calls in try/except
  - [ ] Handle OpenAI-specific exceptions (RateLimitError, APIError, etc.)
  - [ ] Translate OpenAI errors to HTTPException with user-friendly messages
  - [ ] Never log or expose raw API key in errors
  - [ ] Return structured response or raise exception

- [ ] Task 4: Implement chat completion method (AC: #1)

  - [ ] Create generate_chat_completion method
  - [ ] Accept messages, model, temperature parameters
  - [ ] Use GPT-3.5-turbo as default model
  - [ ] Call OpenAI ChatCompletion API
  - [ ] Return response content as string
  - [ ] Handle streaming responses (not MVP, but structure for future)

- [ ] Task 5: Add comprehensive tests (AC: #1)
  - [ ] Create `backend/tests/services/test_openai_service.py`
  - [ ] Mock OpenAI API calls (never call real API in tests)
  - [ ] Test successful API call returns expected response
  - [ ] Test retry logic triggers on 429 and 5xx errors
  - [ ] Test client errors (400, 401) don't retry
  - [ ] Test missing API key raises appropriate error
  - [ ] Test API key decryption failure handling
  - [ ] Test error messages don't expose API key

## Dev Notes

### Critical Architecture Requirements

**Security (CRITICAL):**

- **NEVER** log or expose raw API keys
- API keys loaded from encrypted storage only
- Use user's API key, not system-wide key
- Error messages must not contain API key fragments
- Decryption happens in-memory only, never persisted unencrypted

**Error Handling Patterns:**

- Transient errors (429, 500-503): Retry with backoff
- Client errors (400, 401, 403, 404): No retry, raise immediately
- Network errors: Retry
- Rate limiting: Exponential backoff, inform user
- API key errors: Clear message to user to check configuration

**Service Layer Patterns:**

- Service instantiated per request with user context
- No global/shared OpenAI client (each user has own key)
- Service methods are synchronous (not async) for OpenAI SDK compatibility
- Background tasks use this service for AI operations

### Technical Implementation Details

**File Structure:**

```
backend/app/
├── services/
│   ├── openai_service.py        # NEW - OpenAI service
│   └── encryption_service.py    # EXISTS (from 2.9)
└── tests/services/
    └── test_openai_service.py   # NEW - Service tests
```

**Required Dependencies:**

```python
# backend/requirements.txt (add if not present)
openai>=1.0.0          # OpenAI Python SDK v1.0+
tenacity>=8.0.0        # Retry logic with backoff
```

**OpenAI Service Implementation:**

```python
# backend/app/services/openai_service.py
from typing import List, Dict, Optional
import logging
from openai import OpenAI, RateLimitError, APIError, APIConnectionError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from fastapi import HTTPException, status

from app.models.user import User
from app.services.encryption_service import decrypt_api_key

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for making OpenAI API calls with user's API key."""

    def __init__(self, user: User):
        """
        Initialize OpenAI service with user's encrypted API key.

        Args:
            user: User object containing encrypted OpenAI API key

        Raises:
            HTTPException: If user hasn't configured API key
        """
        if not user.openai_api_key_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "API_KEY_NOT_CONFIGURED",
                    "message": "Please configure your OpenAI API key in settings before using AI features"
                }
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
                    "message": "Failed to decrypt API key. Please reconfigure your API key."
                }
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _make_api_call(self, api_func, **kwargs):
        """
        Make an API call with retry logic.

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

        except RateLimitError as e:
            logger.warning(f"Rate limit hit for user {self.user_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "OPENAI_RATE_LIMIT",
                    "message": "OpenAI rate limit exceeded. Please wait a moment and try again."
                }
            )

        except APIConnectionError as e:
            logger.error(f"OpenAI connection error for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "OPENAI_CONNECTION_ERROR",
                    "message": "Unable to connect to OpenAI. Please check your internet connection and try again."
                }
            )

        except APIError as e:
            logger.error(f"OpenAI API error for user {self.user_id}: {str(e)}")

            # Check for authentication errors (invalid API key)
            if e.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_API_KEY",
                        "message": "Your OpenAI API key is invalid. Please update it in settings."
                    }
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "OPENAI_API_ERROR",
                    "message": f"OpenAI API error: {str(e)}"
                }
            )

        except Exception as e:
            logger.error(f"Unexpected error in OpenAI call for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "UNEXPECTED_ERROR",
                    "message": "An unexpected error occurred. Please try again."
                }
            )

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a chat completion using OpenAI.

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
            "temperature": temperature
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = self._make_api_call(api_func, **kwargs)

        return response.choices[0].message.content
```

**Testing with Mocks:**

```python
# backend/tests/services/test_openai_service.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from openai import RateLimitError, APIError, APIConnectionError
from fastapi import HTTPException

from app.services.openai_service import OpenAIService
from app.models.user import User

@pytest.fixture
def mock_user():
    """Create a mock user with encrypted API key."""
    user = Mock(spec=User)
    user.id = "test-user-id"
    user.openai_api_key_encrypted = b"encrypted_key_data"
    return user

@pytest.fixture
def mock_user_no_key():
    """Create a mock user without API key."""
    user = Mock(spec=User)
    user.id = "test-user-id"
    user.openai_api_key_encrypted = None
    return user

@patch('app.services.openai_service.decrypt_api_key')
@patch('app.services.openai_service.OpenAI')
def test_openai_service_initialization(mock_openai, mock_decrypt, mock_user):
    """Test successful service initialization."""
    mock_decrypt.return_value = "sk-test-key"

    service = OpenAIService(mock_user)

    assert service.user_id == mock_user.id
    mock_decrypt.assert_called_once_with(mock_user.openai_api_key_encrypted)
    mock_openai.assert_called_once_with(api_key="sk-test-key")

def test_openai_service_no_api_key(mock_user_no_key):
    """Test initialization fails when user has no API key."""
    with pytest.raises(HTTPException) as exc_info:
        OpenAIService(mock_user_no_key)

    assert exc_info.value.status_code == 400
    assert "API_KEY_NOT_CONFIGURED" in str(exc_info.value.detail)

@patch('app.services.openai_service.decrypt_api_key')
@patch('app.services.openai_service.OpenAI')
def test_generate_chat_completion_success(mock_openai, mock_decrypt, mock_user):
    """Test successful chat completion."""
    mock_decrypt.return_value = "sk-test-key"

    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Generated response text"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)
    result = service.generate_chat_completion(
        messages=[{"role": "user", "content": "Test prompt"}]
    )

    assert result == "Generated response text"
    mock_client.chat.completions.create.assert_called_once()

@patch('app.services.openai_service.decrypt_api_key')
@patch('app.services.openai_service.OpenAI')
def test_generate_chat_completion_rate_limit(mock_openai, mock_decrypt, mock_user):
    """Test rate limit error handling."""
    mock_decrypt.return_value = "sk-test-key"

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RateLimitError("Rate limit exceeded")
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)

    with pytest.raises(HTTPException) as exc_info:
        service.generate_chat_completion(
            messages=[{"role": "user", "content": "Test"}]
        )

    assert exc_info.value.status_code == 429
    assert "OPENAI_RATE_LIMIT" in str(exc_info.value.detail)

@patch('app.services.openai_service.decrypt_api_key')
@patch('app.services.openai_service.OpenAI')
def test_generate_chat_completion_invalid_key(mock_openai, mock_decrypt, mock_user):
    """Test invalid API key error."""
    mock_decrypt.return_value = "sk-invalid-key"

    mock_client = MagicMock()
    api_error = APIError("Invalid API key")
    api_error.status_code = 401
    mock_client.chat.completions.create.side_effect = api_error
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)

    with pytest.raises(HTTPException) as exc_info:
        service.generate_chat_completion(
            messages=[{"role": "user", "content": "Test"}]
        )

    assert exc_info.value.status_code == 400
    assert "INVALID_API_KEY" in str(exc_info.value.detail)
```

### Dependencies

- Requires User model with openai_api_key_encrypted field (story 2.8)
- Requires encryption service from story 2.9 (decrypt_api_key function)
- Requires openai Python SDK (install via requirements.txt)
- Requires tenacity library for retry logic

### Related Stories

- Story 2.8-2.9: API key storage and encryption (prerequisite)
- Story 4.7: Question generation service (uses this OpenAI service)
- Story 5.2: Feedback analysis service (uses this OpenAI service)
- Story 8.1-8.2: Error handling and retry logic (implements these patterns)

### Performance Considerations

- Service instantiated per request (not singleton)
- Synchronous API calls (OpenAI SDK is sync)
- Retry with exponential backoff prevents overwhelming rate limits
- Max 3 retries keeps response time reasonable
- Background tasks isolate long-running operations from HTTP requests

### Security Considerations

- API keys decrypted only in memory, never persisted
- Logging never includes API keys (even partially)
- Error messages don't expose key fragments
- User-specific keys prevent cross-user data access
- Failed decryption doesn't expose encryption details

### Design Decisions

**Why per-user API keys?**

- User controls their own API costs
- No shared rate limit issues
- User data only sent to their OpenAI account
- Simpler billing and usage tracking

**Why synchronous methods?**

- OpenAI SDK v1.0+ is primarily synchronous
- Background tasks already provide async execution
- Simpler error handling and retry logic
- Async wrapper can be added if needed

**Why tenacity for retries?**

- Industry-standard retry library
- Declarative retry configuration
- Built-in exponential backoff
- Integrates well with logging

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  Security patterns, error handling
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR57, FR58, FR61, NFR-S3

**Key Context Sections:**

- Security Requirements: API key handling, encryption
- Error Handling: Retry logic, user-friendly messages
- Testing: Mocking external APIs, never call real OpenAI in tests
