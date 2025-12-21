"""
Tests for user profile endpoint GET /api/v1/users/me.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_get_profile_without_token_returns_401(
    async_client: AsyncClient,
) -> None:
    """Test that GET /api/v1/users/me without token returns 401."""
    response = await async_client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.asyncio
async def test_get_profile_with_invalid_token_returns_401(
    async_client: AsyncClient,
) -> None:
    """Test that GET /api/v1/users/me with invalid token returns 401."""
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_get_profile_returns_user_data(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that GET /api/v1/users/me returns authenticated user's profile."""
    response = await async_client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Verify returned data matches test user
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email
    assert "created_at" in data

    # Verify password is NEVER included in response
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_get_profile_does_not_expose_password(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that password hash is never exposed in the response."""
    response = await async_client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Ensure no password-related fields are in response
    response_str = str(data).lower()
    assert "password" not in response_str
    assert "hash" not in response_str


@pytest.mark.asyncio
async def test_get_profile_returns_only_authenticated_users_data(
    async_client: AsyncClient,
    db_session,
    auth_headers: dict[str, str],
) -> None:
    """Test that endpoint returns only the authenticated user's data."""
    from app.models.user import User
    from app.core.security import hash_password

    # Create another user in the database
    other_user = User(
        email="other@example.com",
        hashed_password=hash_password("otherpassword123"),
    )
    db_session.add(other_user)
    await db_session.commit()

    # Request with auth_headers (test_user token)
    response = await async_client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Verify we get test_user's data, not other_user's data
    assert data["email"] == "test@example.com"
    assert data["email"] != other_user.email
