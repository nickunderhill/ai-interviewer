"""
Tests for authentication dependency and protected routes.
"""

import uuid

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.models.user import User


def test_missing_token_returns_401(client: TestClient) -> None:
    """Test that requests without a token return 401."""
    response = client.get("/test-protected")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "NOT_AUTHENTICATED"
    assert "Missing bearer token" in data["detail"]["message"]


def test_invalid_token_returns_401(client: TestClient) -> None:
    """Test that requests with invalid token return 401."""
    response = client.get(
        "/test-protected",
        headers={"Authorization": "Bearer invalid_token_string"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TOKEN"


def test_expired_token_returns_401(client: TestClient) -> None:
    """Test that expired tokens return 401."""
    from datetime import datetime, timedelta, timezone
    from jose import jwt
    from app.core.config import settings

    # Create an expired token
    payload = {
        "user_id": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # Expired 1 hour ago
    }
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    response = client.get(
        "/test-protected",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TOKEN"
    assert "expired" in data["detail"]["message"].lower()


def test_token_without_user_id_returns_401(client: TestClient) -> None:
    """Test that token missing user_id returns 401."""
    from jose import jwt
    from app.core.config import settings
    from datetime import datetime, timedelta, timezone

    # Create token without user_id
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "some_other_field": "value",
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    response = client.get(
        "/test-protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TOKEN"


def test_token_with_invalid_user_id_format_returns_401(client: TestClient) -> None:
    """Test that token with invalid UUID format returns 401."""
    token = create_access_token({"user_id": "not-a-valid-uuid"})

    response = client.get(
        "/test-protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TOKEN"
    assert "format" in data["detail"]["message"].lower()


@pytest.mark.asyncio
async def test_token_with_nonexistent_user_returns_401(
    async_client: AsyncClient,
) -> None:
    """Test that valid token with non-existent user returns 401."""
    # Create token for a user that doesn't exist in DB
    nonexistent_user_id = uuid.uuid4()
    token = create_access_token({"user_id": str(nonexistent_user_id)})

    response = await async_client.get(
        "/test-protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "USER_NOT_FOUND"


@pytest.mark.asyncio
async def test_valid_token_authenticates(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """Test that valid token successfully authenticates and returns user data."""
    response = await async_client.get("/test-protected", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(test_user.id)
    assert data["email"] == test_user.email


# Test endpoint for dependency testing
def create_test_protected_endpoint(app: FastAPI) -> None:
    """Helper to add a test endpoint that uses the get_current_user dependency."""
    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/test-protected")
    async def test_protected(current_user: User = Depends(get_current_user)):
        return {
            "user_id": str(current_user.id),
            "email": current_user.email,
        }

    app.include_router(router)
