"""
Tests for POST /api/v1/resumes endpoint.
"""

from httpx import AsyncClient
import pytest

from app.models.user import User


@pytest.mark.asyncio
async def test_create_resume_success(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test successful resume creation returns 201."""
    resume_data = {
        "content": "# My Resume\n\nExperience: 5 years in Python development\nSkills: Python, FastAPI, PostgreSQL"
    }

    response = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == resume_data["content"]
    assert data["user_id"] == str(test_user.id)
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_resume_duplicate_returns_409(
    async_client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test creating duplicate resume returns 409 Conflict."""
    resume_data = {"content": "First resume content"}

    # Create first resume
    response1 = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        headers=auth_headers,
    )
    assert response1.status_code == 201

    # Attempt to create second resume (should fail)
    resume_data2 = {"content": "Second resume content"}
    response2 = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data2,
        headers=auth_headers,
    )

    assert response2.status_code == 409
    assert "already has a resume" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_create_resume_empty_content_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test empty content returns 422 Validation Error."""
    resume_data = {"content": ""}

    response = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        headers=auth_headers,
    )

    assert response.status_code == 422
    assert "string_too_short" in response.json()["detail"][0]["type"]


@pytest.mark.asyncio
async def test_create_resume_content_too_long_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test content exceeding max length returns 422."""
    # Create content longer than 50,000 characters
    resume_data = {"content": "x" * 50001}

    response = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_resume_unauthenticated_returns_401(async_client: AsyncClient):
    """Test unauthenticated request returns 401."""
    resume_data = {"content": "Test resume content"}

    response = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        # No auth headers
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_resume_with_unicode_content(
    async_client: AsyncClient, auth_headers: dict
):
    """Test resume with unicode characters is handled correctly."""
    resume_data = {
        "content": "Name: José García\nSkills: Python, 日本語, العربية\n🎓 Education"
    }

    response = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == resume_data["content"]


@pytest.mark.asyncio
async def test_create_resume_with_large_valid_content(
    async_client: AsyncClient, auth_headers: dict
):
    """Test resume with large but valid content (near max length)."""
    # Create content close to but under 50,000 characters
    large_content = "Experience:\n" + ("Detail about my work. " * 2270)  # ~49,600 chars

    resume_data = {"content": large_content}

    response = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data["content"]) < 50000
    assert len(data["content"]) > 45000


@pytest.mark.asyncio
async def test_create_resume_whitespace_only_passes_validation(
    async_client: AsyncClient, auth_headers: dict
):
    """Test whitespace-only content passes validation (min_length counts whitespace)."""
    # Pydantic min_length=1 allows whitespace-only strings
    # This is a known behavior - length includes whitespace
    resume_data = {"content": "   \n\t  "}

    response = await async_client.post(
        "/api/v1/resumes/",
        json=resume_data,
        headers=auth_headers,
    )

    # Currently passes validation - Pydantic counts whitespace as length
    # Future enhancement: Add custom validator to strip and check
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "   \n\t  "
