# Story 8.5: Implement Secure API Key Storage and Validation

Status: in-progress

## Story

As a developer, I want to ensure OpenAI API keys are securely stored and
validated, so that user credentials are protected and functional.

## Acceptance Criteria

1. **Given** a user configures their OpenAI API key **When** the key is saved
   **Then** it's encrypted using AES-256 (Fernet) before database storage
   **And** the encryption key is stored in environment variables (not in code)
   **And** the system validates the key format (starts with 'sk-') before
   encryption **And** decrypts the key only at runtime when making OpenAI calls
   **And** the raw key is never logged or exposed in API responses **And** the
   database field is encrypted at rest **And** follows OWASP security best
   practices (NFR4, NFR5, NFR10, FR62) ✅

## Tasks / Subtasks

- [ ] Task 1: Verify encryption service exists from Story 2.9 (AC: #1)

  - [ ] Check `backend/app/services/encryption_service.py` exists
  - [ ] Verify Fernet (AES-256) encryption is implemented
  - [ ] Confirm encryption key comes from environment variable
  - [ ] Ensure encrypt/decrypt functions work correctly

- [ ] Task 2: Implement API key format validation (AC: #1)

  - [ ] Create validation function in `backend/app/utils/validators.py`
  - [ ] Check key starts with 'sk-'
  - [ ] Validate minimum length (40+ characters for OpenAI keys)
  - [ ] Raise descriptive error for invalid format
  - [ ] Add to Pydantic schema validation

- [ ] Task 3: Add API key validation test endpoint (AC: #1)

  - [ ] Create POST `/api/v1/users/me/api-key/validate` endpoint
  - [ ] Accept API key in request body
  - [ ] Test OpenAI connection with provided key
  - [ ] Return success/failure without storing key
  - [ ] Use for pre-save validation in frontend

- [ ] Task 4: Audit existing API key endpoints for security (AC: #1)

  - [ ] Review POST `/api/v1/users/me/api-key` (from Story 2.10)
  - [ ] Review PUT `/api/v1/users/me/api-key` (from Story 2.11)
  - [ ] Ensure encryption before database write
  - [ ] Verify raw key never appears in logs
  - [ ] Check error messages don't leak key information

- [ ] Task 5: Implement secure key retrieval for OpenAI service (AC: #1)

  - [ ] Update `openai_service.py` to decrypt key at runtime
  - [ ] Never cache decrypted keys in memory longer than needed
  - [ ] Clear sensitive variables after use
  - [ ] Use context managers for key lifecycle

- [ ] Task 6: Add security headers and response filtering (AC: #1)
  - [ ] Ensure User schema never includes encrypted_api_key field
  - [ ] Add response model validation to prevent key leakage
  - [ ] Review all user-related endpoints for key exposure
  - [ ] Add integration tests for security

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Encryption:** AES-256 via Fernet (cryptography library)
- **Key Storage:** Environment variable `ENCRYPTION_KEY`
- **Validation:** Format check before encryption
- **Decryption:** Only at runtime, never cached
- **Logging:** Never log raw or encrypted keys

**Security Standards:**

- OWASP best practices for credential storage
- No key exposure in API responses
- No key logging (raw or encrypted)
- Encryption key rotation support

### File Structure

```
backend/app/
├── services/
│   └── encryption_service.py  # Already exists from Story 2.9
├── utils/
│   └── validators.py          # Add API key format validation
├── api/v1/endpoints/
│   └── users.py               # Audit existing endpoints, add validate endpoint
└── schemas/
    └── user.py                # Ensure no api_key exposure
```

### Implementation Details

**API Key Validation:**

```python
# backend/app/utils/validators.py
import re

def validate_openai_api_key_format(api_key: str) -> bool:
    """
    Validate OpenAI API key format.

    OpenAI keys typically:
    - Start with 'sk-'
    - Contain 40+ alphanumeric characters

    Args:
        api_key: The API key to validate

    Returns:
        True if valid format, False otherwise

    Raises:
        ValueError: If format is invalid with descriptive message
    """
    if not api_key:
        raise ValueError("API key cannot be empty")

    if not api_key.startswith("sk-"):
        raise ValueError("OpenAI API key must start with 'sk-'")

    if len(api_key) < 40:
        raise ValueError("API key appears to be too short")

    # Check for valid characters (alphanumeric and hyphens)
    if not re.match(r'^sk-[A-Za-z0-9\-_]+$', api_key):
        raise ValueError("API key contains invalid characters")

    return True
```

**API Key Validation Endpoint:**

```python
# backend/app/api/v1/endpoints/users.py (add this endpoint)
from openai import AsyncOpenAI
from app.utils.validators import validate_openai_api_key_format

@router.post("/me/api-key/validate")
async def validate_api_key(
    api_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    Validate OpenAI API key without saving it.
    Tests format and makes a test API call.
    """
    try:
        # Format validation
        validate_openai_api_key_format(api_key)

        # Test actual connection
        client = AsyncOpenAI(api_key=api_key)

        # Make a minimal API call to verify key works
        # Using a very cheap operation (list models)
        await client.models.list()

        return {
            "valid": True,
            "message": "API key is valid and working"
        }

    except ValueError as e:
        return {
            "valid": False,
            "message": str(e)
        }
    except Exception as e:
        logger.warning(f"API key validation failed: {e}")
        return {
            "valid": False,
            "message": "API key validation failed. Please check the key and try again."
        }
```

**Secure Key Decryption in OpenAI Service:**

```python
# backend/app/services/openai_service.py (update)
from app.services.encryption_service import decrypt_api_key
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Service for OpenAI API interactions with secure key handling.
    """

    @staticmethod
    async def get_client_for_user(user: User) -> AsyncOpenAI:
        """
        Get OpenAI client with decrypted user API key.

        Args:
            user: User model with encrypted_api_key field

        Returns:
            Configured AsyncOpenAI client

        Raises:
            ValueError: If user has no API key configured
        """
        if not user.encrypted_api_key:
            raise ValueError("No OpenAI API key configured for this user")

        try:
            # Decrypt key at runtime
            api_key = decrypt_api_key(user.encrypted_api_key)

            # Create client (key lives only in this scope)
            client = AsyncOpenAI(api_key=api_key)

            # Clear decrypted key from memory ASAP
            del api_key

            return client

        except Exception as e:
            logger.error("Failed to decrypt API key", extra={
                "user_id": str(user.id),
                "error": str(e)
            })
            raise ValueError("Failed to decrypt API key")

    @staticmethod
    async def generate_completion(user: User, prompt: str, **kwargs) -> str:
        """
        Generate completion with secure key handling.
        """
        client = await OpenAIService.get_client_for_user(user)

        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        finally:
            # Cleanup (client will be garbage collected)
            del client
```

**Audit Existing Endpoints:**

```python
# backend/app/api/v1/endpoints/users.py (verify these exist from Stories 2.10, 2.11)
from app.utils.validators import validate_openai_api_key_format
from app.services.encryption_service import encrypt_api_key

@router.post("/me/api-key")
async def configure_api_key(
    api_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Configure OpenAI API key (from Story 2.10)"""
    # Validate format BEFORE encryption
    validate_openai_api_key_format(api_key)

    # Encrypt before storage
    encrypted_key = encrypt_api_key(api_key)

    # Clear plaintext key from memory
    del api_key

    # Store encrypted key
    current_user.encrypted_api_key = encrypted_key
    await db.commit()

    # NEVER log the key
    logger.info(f"API key configured for user {current_user.id}")

    return {"message": "API key configured successfully"}

@router.put("/me/api-key")
async def update_api_key(
    api_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update OpenAI API key (from Story 2.11)"""
    # Same security measures as configure
    validate_openai_api_key_format(api_key)
    encrypted_key = encrypt_api_key(api_key)
    del api_key

    current_user.encrypted_api_key = encrypted_key
    await db.commit()

    logger.info(f"API key updated for user {current_user.id}")
    return {"message": "API key updated successfully"}
```

**User Schema - Ensure No Key Exposure:**

```python
# backend/app/schemas/user.py
from pydantic import BaseModel

class UserResponse(BaseModel):
    """User response schema - NEVER include encrypted_api_key"""
    id: str
    email: str
    created_at: datetime
    has_api_key: bool  # Boolean flag instead of actual key

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, user):
        return cls(
            id=str(user.id),
            email=user.email,
            created_at=user.created_at,
            has_api_key=bool(user.encrypted_api_key)
        )
```

**Environment Configuration:**

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... other settings ...

    # Encryption key for API keys (must be 32 bytes for Fernet)
    ENCRYPTION_KEY: str

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Validate encryption key format
        if not self.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY must be set in environment")

        # Key should be base64 encoded 32 bytes
        from cryptography.fernet import Fernet
        try:
            Fernet(self.ENCRYPTION_KEY.encode())
        except Exception:
            raise ValueError("ENCRYPTION_KEY must be a valid Fernet key")
```

### Testing Requirements

**Test Coverage:**

- API key format validation catches invalid formats
- Encryption/decryption round-trip works
- Validation endpoint works without saving key
- User schema never exposes encrypted_api_key
- Logs never contain raw or encrypted keys
- Error messages don't leak key information

**Test Files:**

- `backend/tests/utils/test_validators.py`
- `backend/tests/api/v1/test_users_api_key_security.py`
- `backend/tests/services/test_encryption_service.py`

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.5]
- [Source: Story 2.9 - Encryption service implementation]
- [Source: Story 2.10, 2.11 - API key endpoints]
- [NFR4, NFR5, NFR10: Security requirements]
- [FR62: Never expose API keys to frontend]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with comprehensive API key security
- Validation before encryption
- Secure decryption at runtime
- No key exposure in logs or responses
- Ready for dev implementation
