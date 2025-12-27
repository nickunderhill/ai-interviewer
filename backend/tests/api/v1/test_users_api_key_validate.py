"""
Tests for API key validation endpoint POST /api/v1/users/me/api-key/validate.
"""

from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
import pytest

from app.models.user import User


@pytest.mark.asyncio
async def test_validate_api_key_without_authentication_returns_401(
    async_client: AsyncClient,
) -> None:
    """Test that POST /api/v1/users/me/api-key/validate without token returns 401."""
    response = await async_client.post(
        "/api/v1/users/me/api-key/validate",
        json={"api_key": "sk-test123456789012345678901234567890"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.asyncio
async def test_validate_api_key_with_invalid_token_returns_401(
    async_client: AsyncClient,
) -> None:
    """Test that POST /api/v1/users/me/api-key/validate with invalid token returns 401."""
    response = await async_client.post(
        "/api/v1/users/me/api-key/validate",
        headers={"Authorization": "Bearer invalid_token"},
        json={"api_key": "sk-test123456789012345678901234567890"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_validate_api_key_with_invalid_format_returns_400(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that validation fails for API key with invalid format."""
    # Missing sk- prefix
    response = await async_client.post(
        "/api/v1/users/me/api-key/validate",
        headers=auth_headers,
        json={"api_key": "invalid_key_format"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_API_KEY_FORMAT"
    assert "must start with 'sk-'" in data["detail"]["message"]


@pytest.mark.asyncio
async def test_validate_api_key_too_short_returns_400(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that validation fails for API key that's too short."""
    response = await async_client.post(
        "/api/v1/users/me/api-key/validate",
        headers=auth_headers,
        json={"api_key": "sk-short"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_API_KEY_FORMAT"
    assert "too short" in data["detail"]["message"]


@pytest.mark.asyncio
async def test_validate_api_key_with_valid_key_returns_success(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that validation succeeds with valid OpenAI API key."""
    with patch("app.api.v1.endpoints.users.AsyncOpenAI") as mock_openai:
        # Mock successful OpenAI API call
        mock_client = AsyncMock()
        mock_client.models.list = AsyncMock(return_value=[])
        mock_openai.return_value = mock_client

        response = await async_client.post(
            "/api/v1/users/me/api-key/validate",
            headers=auth_headers,
            json={"api_key": "sk-proj-test123456789012345678901234567890"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "valid and working" in data["message"]


@pytest.mark.asyncio
async def test_validate_api_key_with_invalid_openai_key_returns_failure(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that validation fails when OpenAI rejects the API key."""
    with patch("app.api.v1.endpoints.users.AsyncOpenAI") as mock_openai:
        # Mock OpenAI 401 error
        mock_client = AsyncMock()
        mock_client.models.list = AsyncMock(
            side_effect=Exception("401 Incorrect API key provided")
        )
        mock_openai.return_value = mock_client

        response = await async_client.post(
            "/api/v1/users/me/api-key/validate",
            headers=auth_headers,
            json={"api_key": "sk-proj-invalid123456789012345678901234567890"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Invalid API key" in data["message"]


@pytest.mark.asyncio
async def test_validate_api_key_with_rate_limit_error(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that validation handles rate limit errors gracefully."""
    with patch("app.api.v1.endpoints.users.AsyncOpenAI") as mock_openai:
        # Mock OpenAI 429 rate limit error
        mock_client = AsyncMock()
        mock_client.models.list = AsyncMock(
            side_effect=Exception("429 Rate limit exceeded")
        )
        mock_openai.return_value = mock_client

        response = await async_client.post(
            "/api/v1/users/me/api-key/validate",
            headers=auth_headers,
            json={"api_key": "sk-proj-test123456789012345678901234567890"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Rate limit exceeded" in data["message"]


@pytest.mark.asyncio
async def test_validate_api_key_with_network_error(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Test that validation handles network errors gracefully."""
    with patch("app.api.v1.endpoints.users.AsyncOpenAI") as mock_openai:
        # Mock network error
        mock_client = AsyncMock()
        mock_client.models.list = AsyncMock(side_effect=Exception("Connection timeout"))
        mock_openai.return_value = mock_client

        response = await async_client.post(
            "/api/v1/users/me/api-key/validate",
            headers=auth_headers,
            json={"api_key": "sk-proj-test123456789012345678901234567890"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Could not validate API key" in data["message"]


@pytest.mark.asyncio
async def test_validate_api_key_does_not_store_key(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
) -> None:
    """Test that validation does not store the API key in the database."""
    original_key = test_user.encrypted_api_key

    with patch("app.api.v1.endpoints.users.AsyncOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_client.models.list = AsyncMock(return_value=[])
        mock_openai.return_value = mock_client

        response = await async_client.post(
            "/api/v1/users/me/api-key/validate",
            headers=auth_headers,
            json={"api_key": "sk-proj-test123456789012345678901234567890"},
        )

        assert response.status_code == 200

        # Verify user's API key was not changed
        assert test_user.encrypted_api_key == original_key
