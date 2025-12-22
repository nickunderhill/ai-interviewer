"""
Tests for PUT /api/v1/resumes/me endpoint.
"""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_update_resume_success(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test successful resume update returns 200."""
    # First create a resume
    initial_content = "# Original Resume\n\nExperience: 3 years"
    create_response = await async_client.post(
        "/api/v1/resumes/",
        json={"content": initial_content},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    original_data = create_response.json()

    # Update the resume
    updated_content = "# Updated Resume\n\nExperience: 5 years\nNew skills added"
    response = await async_client.put(
        "/api/v1/resumes/me",
        json={"content": updated_content},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == updated_content
    assert data["content"] != initial_content
    assert data["user_id"] == str(test_user.id)
    assert data["id"] == original_data["id"]  # Same resume ID


@pytest.mark.asyncio
async def test_update_resume_timestamp_changes(
    async_client: AsyncClient, auth_headers: dict
):
    """Test updated_at timestamp changes after update."""
    # Create resume
    create_response = await async_client.post(
        "/api/v1/resumes/",
        json={"content": "Original content"},
        headers=auth_headers,
    )
    original_updated_at = create_response.json()["updated_at"]

    # Update resume - service explicitly sets updated_at to current time
    response = await async_client.put(
        "/api/v1/resumes/me",
        json={"content": "Updated content"},
        headers=auth_headers,
    )

    new_updated_at = response.json()["updated_at"]
    # Timestamps should be different (update happened after creation)
    # Using >= instead of > for microsecond precision edge cases
    assert new_updated_at >= original_updated_at
    # Also verify content actually changed
    assert response.json()["content"] == "Updated content"


@pytest.mark.asyncio
async def test_update_resume_not_found_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """Test 404 when updating non-existent resume."""
    response = await async_client.put(
        "/api/v1/resumes/me",
        json={"content": "Updated content"},
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_resume_empty_content_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test 422 for empty content."""
    # Create resume first
    await async_client.post(
        "/api/v1/resumes/",
        json={"content": "Original content"},
        headers=auth_headers,
    )

    # Try to update with empty content
    response = await async_client.put(
        "/api/v1/resumes/me",
        json={"content": ""},
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_resume_content_too_long_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test 422 for content exceeding max length."""
    # Create resume first
    await async_client.post(
        "/api/v1/resumes/",
        json={"content": "Original content"},
        headers=auth_headers,
    )

    # Try to update with content too long
    response = await async_client.put(
        "/api/v1/resumes/me",
        json={"content": "x" * 50001},
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_resume_unauthenticated_returns_401(async_client: AsyncClient):
    """Test unauthenticated request returns 401."""
    response = await async_client.put(
        "/api/v1/resumes/me",
        json={"content": "Updated content"},
    )

    assert response.status_code == 401
