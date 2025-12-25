"""
Tests for DELETE /api/v1/resumes/me endpoint.
"""

from httpx import AsyncClient
import pytest

from app.models.user import User


@pytest.mark.asyncio
async def test_delete_resume_success(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test successful deletion returns 204."""
    # First create a resume
    create_response = await async_client.post(
        "/api/v1/resumes/",
        json={"content": "Resume to delete"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    # Delete the resume
    response = await async_client.delete(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""  # No content in response


@pytest.mark.asyncio
async def test_get_after_delete_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """Test subsequent GET after DELETE returns 404."""
    # Create resume
    await async_client.post(
        "/api/v1/resumes/",
        json={"content": "Resume to delete"},
        headers=auth_headers,
    )

    # Verify it exists
    get_response = await async_client.get(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )
    assert get_response.status_code == 200

    # Delete it
    delete_response = await async_client.delete(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    # Try to get it again - should be 404
    get_after_delete = await async_client.get(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_delete_resume_not_found_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """Test 404 when deleting non-existent resume."""
    response = await async_client.delete(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_resume_unauthenticated_returns_401(async_client: AsyncClient):
    """Test unauthenticated request returns 401."""
    response = await async_client.delete("/api/v1/resumes/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_recreate_after_delete(async_client: AsyncClient, auth_headers: dict):
    """Test user can create new resume after deletion."""
    # Create, delete, then create again
    await async_client.post(
        "/api/v1/resumes/",
        json={"content": "First resume"},
        headers=auth_headers,
    )

    await async_client.delete("/api/v1/resumes/me", headers=auth_headers)

    # Should be able to create again
    create_response = await async_client.post(
        "/api/v1/resumes/",
        json={"content": "Second resume after deletion"},
        headers=auth_headers,
    )

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["content"] == "Second resume after deletion"
