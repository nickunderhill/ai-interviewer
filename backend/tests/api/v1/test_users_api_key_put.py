"""
Tests for API key update endpoint PUT /api/v1/users/me/api-key.
"""

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.encryption_service import decrypt_api_key, encrypt_api_key


@pytest.mark.asyncio
async def test_update_api_key_requires_authentication(
    async_client: AsyncClient,
) -> None:
    """Test that PUT /api/v1/users/me/api-key requires authentication."""
    response = await async_client.put(
        "/api/v1/users/me/api-key",
        json={"api_key": "sk-new-test-key"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.asyncio
async def test_update_api_key_with_invalid_token_returns_401(
    async_client: AsyncClient,
) -> None:
    """Test that invalid token returns 401."""
    response = await async_client.put(
        "/api/v1/users/me/api-key",
        headers={"Authorization": "Bearer invalid_token"},
        json={"api_key": "sk-new-test-key"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_update_api_key_overwrites_existing_encrypted_key(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """Test that updating API key overwrites the existing encrypted key."""
    # First, set an initial API key
    initial_key = "sk-initial-test-key-1234567890123456789012"
    test_user.encrypted_api_key = encrypt_api_key(initial_key)
    await db_session.commit()
    await db_session.refresh(test_user)

    # Store the initial encrypted value
    initial_encrypted = test_user.encrypted_api_key

    # Now update with a new key
    new_key = "sk-new-updated-key-6789012345678901234567890"
    response = await async_client.put(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": new_key},
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "successfully" in data["message"].lower() or "updated" in data["message"].lower()

    # Verify the encrypted key was overwritten
    await db_session.refresh(test_user)
    assert test_user.encrypted_api_key is not None
    assert test_user.encrypted_api_key != initial_encrypted

    # Verify the new key can be decrypted to the correct value
    decrypted = decrypt_api_key(test_user.encrypted_api_key)
    assert decrypted == new_key


@pytest.mark.asyncio
async def test_update_api_key_response_does_not_contain_api_key(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """Test that the response never contains the API key."""
    # Set initial key
    test_user.encrypted_api_key = encrypt_api_key("sk-initial-key-1234567890123456789012345678")
    await db_session.commit()

    # Update with new key
    new_key = "sk-secret-new-key-9999901234567890123456789"
    response = await async_client.put(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": new_key},
    )

    assert response.status_code == 200
    data = response.json()

    # Ensure API key is not in response
    response_str = str(data).lower()
    assert new_key not in response_str
    assert "sk-" not in response_str
    assert "api_key" not in response_str or data.get("api_key") is None


@pytest.mark.asyncio
async def test_update_api_key_works_when_no_existing_key(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """Test that updating works even if user has no existing API key (acts like initial set)."""
    # Ensure user has no API key
    test_user.encrypted_api_key = None
    await db_session.commit()
    await db_session.refresh(test_user)
    assert test_user.encrypted_api_key is None

    # Update (which is effectively setting for first time)
    new_key = "sk-first-time-key-1111101234567890123456789"
    response = await async_client.put(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": new_key},
    )

    assert response.status_code == 200

    # Verify key was stored
    await db_session.refresh(test_user)
    assert test_user.encrypted_api_key is not None
    decrypted = decrypt_api_key(test_user.encrypted_api_key)
    assert decrypted == new_key


@pytest.mark.asyncio
async def test_update_api_key_with_empty_string_fails(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """Test that empty API key is rejected."""
    # Set initial key
    test_user.encrypted_api_key = encrypt_api_key("sk-initial-0123456789012345678901234567890")
    await db_session.commit()

    # Try to update with empty string
    response = await async_client.put(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": ""},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_api_key_stores_encrypted_not_plaintext(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """Test that API key is stored encrypted, not as plaintext."""
    plaintext_key = "sk-plaintext-test-key-9999901234567890123456"

    response = await async_client.put(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": plaintext_key},
    )

    assert response.status_code == 200

    # Verify encryption
    await db_session.refresh(test_user)
    stored_value = test_user.encrypted_api_key

    # Stored value should not be the plaintext
    assert stored_value != plaintext_key

    # Stored value should not contain the plaintext
    assert plaintext_key not in stored_value

    # But it should decrypt to the plaintext
    decrypted = decrypt_api_key(stored_value)
    assert decrypted == plaintext_key
