"""
Smoke tests for FastAPI application endpoints.
Updated to test database integration.
"""

from httpx import ASGITransport, AsyncClient
import pytest

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test that root endpoint returns running status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AI Interviewer API"
        assert data["status"] == "running"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test that health check endpoint verifies database connectivity."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "api" in data
        assert data["api"] == "operational"
        # Database status should be "connected" if PostgreSQL is running
        assert data["database"] == "connected"
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_v1_endpoint():
    """Test that v1 health check endpoint returns healthy status."""
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
