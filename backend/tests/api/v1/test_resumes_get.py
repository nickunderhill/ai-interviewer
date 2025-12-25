"""
Tests for GET /api/v1/resumes/me endpoint.
"""

from httpx import AsyncClient
import pytest

from app.models.user import User


@pytest.mark.asyncio
async def test_get_resume_success(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test successful resume retrieval returns 200."""
    # First create a resume
    resume_data = {"content": "# My Resume\n\nExperience: Senior Developer"}
    create_response = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    # Now retrieve it
    response = await async_client.get(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == resume_data["content"]
    assert data["user_id"] == str(test_user.id)
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_resume_not_found_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """Test 404 when user has no resume."""
    response = await async_client.get(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_resume_unauthenticated_returns_401(async_client: AsyncClient):
    """Test unauthenticated request returns 401."""
    response = await async_client.get("/api/v1/resumes/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_cannot_access_other_users_resume(
    async_client: AsyncClient,
    test_user: User,
    auth_headers: dict,
    db_session,
):
    """Test user isolation - users can only see their own resume."""
    from app.models.resume import Resume
    from app.models.user import User

    # Create another user with a resume
    other_user = User(
        email="other@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_resume = Resume(
        user_id=other_user.id,
        content="Other user's secret resume",
    )
    db_session.add(other_resume)
    await db_session.commit()

    # Test user tries to get their resume (should get 404 since they don't have one)
    response = await async_client.get(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )

    assert response.status_code == 404  # test_user has no resume

    # Create resume for test_user
    await async_client.post(
        "/api/v1/resumes/",
        json={"content": "Test user's resume"},
        headers=auth_headers,
    )

    # Get test_user's resume
    response = await async_client.get(
        "/api/v1/resumes/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    # Should get test_user's resume, not other_user's
    assert data["content"] == "Test user's resume"
    assert data["content"] != "Other user's secret resume"
