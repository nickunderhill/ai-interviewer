"""
Smoke tests for FastAPI application endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test that root endpoint returns operational status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AI Interviewer API"
        assert data["status"] == "operational"
        assert "version" in data


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test that health check endpoint returns healthy status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint_returns_dict():
    """Test that root endpoint returns a dictionary structure."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)


@pytest.mark.asyncio
async def test_health_check_returns_dict():
    """Test that health check endpoint returns a dictionary structure."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
