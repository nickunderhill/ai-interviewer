"""
Tests for POST /api/v1/job-postings endpoint.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_job_posting_success(
    async_client: AsyncClient, auth_headers: dict
):
    """Test successful job posting creation returns 201."""
    job_posting_data = {
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "description": "We are looking for a Senior Python Developer with 5+ years of experience...",
        "experience_level": "Senior",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    }

    response = await async_client.post(
        "/api/v1/job-postings/",
        json=job_posting_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Senior Python Developer"
    assert data["company"] == "Tech Corp"
    assert "Python Developer" in data["description"]
    assert data["experience_level"] == "Senior"
    assert data["tech_stack"] == ["Python", "FastAPI", "PostgreSQL", "Docker"]
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_job_posting_only_required_fields(
    async_client: AsyncClient, auth_headers: dict
):
    """Test creating job posting with only required fields."""
    job_posting_data = {
        "title": "Backend Developer",
        "description": "Backend development position",
    }

    response = await async_client.post(
        "/api/v1/job-postings/",
        json=job_posting_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Backend Developer"
    assert data["description"] == "Backend development position"
    assert data["company"] is None
    assert data["experience_level"] is None
    assert data["tech_stack"] == []  # Now defaults to empty list


@pytest.mark.asyncio
async def test_create_job_posting_missing_title_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test missing required title returns 422."""
    job_posting_data = {
        "description": "Description without title",
    }

    response = await async_client.post(
        "/api/v1/job-postings/",
        json=job_posting_data,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_job_posting_empty_title_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test empty title returns 422."""
    job_posting_data = {
        "title": "",
        "description": "Description",
    }

    response = await async_client.post(
        "/api/v1/job-postings/",
        json=job_posting_data,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_job_posting_title_too_long_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test title exceeding max length returns 422."""
    job_posting_data = {
        "title": "x" * 256,  # Max is 255
        "description": "Description",
    }

    response = await async_client.post(
        "/api/v1/job-postings/",
        json=job_posting_data,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_job_posting_description_too_long_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test description exceeding max length returns 422."""
    job_posting_data = {
        "title": "Test Position",
        "description": "x" * 10001,  # Max is 10000
    }

    response = await async_client.post(
        "/api/v1/job-postings/",
        json=job_posting_data,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_job_posting_unauthenticated_returns_401(
    async_client: AsyncClient,
):
    """Test unauthenticated request returns 401."""
    job_posting_data = {
        "title": "Test Position",
        "description": "Test description",
    }

    response = await async_client.post(
        "/api/v1/job-postings/",
        json=job_posting_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_multiple_job_postings(
    async_client: AsyncClient, auth_headers: dict
):
    """Test user can create multiple job postings."""
    # Create first job posting
    response1 = await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Position 1", "description": "Description 1"},
        headers=auth_headers,
    )
    assert response1.status_code == 201

    # Create second job posting
    response2 = await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Position 2", "description": "Description 2"},
        headers=auth_headers,
    )
    assert response2.status_code == 201

    # IDs should be different
    assert response1.json()["id"] != response2.json()["id"]
