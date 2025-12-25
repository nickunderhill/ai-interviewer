"""
Tests for API key configuration endpoint POST /api/v1/users/me/api-key.
"""

from httpx import AsyncClient
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.encryption_service import decrypt_api_key


@pytest.mark.asyncio
async def test_set_api_key_without_authentication_returns_401(
    async_client: AsyncClient,
) -> None:
    """Test that POST /api/v1/users/me/api-key without token returns 401."""
    response = await async_client.post(
        "/api/v1/users/me/api-key",
        json={"api_key": "sk-test123"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.asyncio
async def test_set_api_key_with_invalid_token_returns_401(
    async_client: AsyncClient,
) -> None:
    """Test that POST /api/v1/users/me/api-key with invalid token returns 401."""
    response = await async_client.post(
        "/api/v1/users/me/api-key",
        headers={"Authorization": "Bearer invalid_token"},
        json={"api_key": "sk-test123"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_set_api_key_successfully_stores_encrypted_value(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """Test that API key is encrypted and stored successfully."""
    api_key = "sk-proj-testkey123456789"

    response = await async_client.post(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": api_key},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "API key configured successfully"

    # Verify the API key is stored in encrypted form
    result = await db_session.execute(select(User).where(User.id == test_user.id))
    user = result.scalar_one()

    # Should have encrypted value, not plaintext
    assert user.encrypted_api_key is not None
    assert user.encrypted_api_key != api_key  # Should be encrypted

    # Decrypt and verify it matches the original
    decrypted = decrypt_api_key(user.encrypted_api_key)
    assert decrypted == api_key


@pytest.mark.asyncio
async def test_set_api_key_response_does_not_contain_api_key(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that API key is never included in response."""
    api_key = "sk-proj-secretkey987654321"

    response = await async_client.post(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": api_key},
    )

    assert response.status_code == 200
    response_text = response.text

    # API key should not appear anywhere in response
    assert api_key not in response_text
    assert "secretkey" not in response_text
    assert "sk-proj" not in response_text


@pytest.mark.asyncio
async def test_set_api_key_stores_plaintext_not_in_database(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """Test that plaintext API key is never stored in database."""
    api_key = "sk-test-plaintext-should-not-be-stored"

    response = await async_client.post(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": api_key},
    )

    assert response.status_code == 200

    # Check database directly - plaintext should not exist
    result = await db_session.execute(select(User).where(User.id == test_user.id))
    user = result.scalar_one()

    # Verify encrypted value doesn't contain plaintext substring
    assert api_key not in user.encrypted_api_key
    assert "plaintext" not in user.encrypted_api_key


@pytest.mark.asyncio
async def test_set_api_key_can_update_existing_key(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    """Test that API key can be updated/replaced."""
    # Set initial key
    first_key = "sk-test-first-key"
    await async_client.post(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": first_key},
    )

    # Update with new key
    second_key = "sk-test-second-key"
    response = await async_client.post(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": second_key},
    )

    assert response.status_code == 200

    # Verify new key is stored
    result = await db_session.execute(select(User).where(User.id == test_user.id))
    user = result.scalar_one()

    decrypted = decrypt_api_key(user.encrypted_api_key)
    assert decrypted == second_key
    assert decrypted != first_key


@pytest.mark.asyncio
async def test_set_api_key_with_empty_string_fails(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that empty API key is rejected."""
    response = await async_client.post(
        "/api/v1/users/me/api-key",
        headers=auth_headers,
        json={"api_key": ""},
    )

    # Should fail validation
    assert response.status_code == 422
