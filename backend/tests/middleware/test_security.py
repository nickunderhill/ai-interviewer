from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_cors_allowed_origin():
    """Test that CORS allows requests from the configured frontend origin."""
    response = client.options(
        "/",
        headers={
            "Origin": settings.FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == settings.FRONTEND_ORIGIN
    assert "GET" in response.headers["access-control-allow-methods"]


def test_cors_rejected_origin():
    """Test that CORS rejects requests from unauthorized origins."""
    # Note: TestClient doesn't enforce CORS blocking like a browser,
    # but we can check that the Access-Control-Allow-Origin header is missing or doesn't match.
    # However, FastAPI's CORSMiddleware usually just doesn't send the header if origin is not allowed.

    response = client.options(
        "/",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # If origin is not allowed, FastAPI/Starlette CORS middleware typically returns 400 or doesn't set the header.
    # In recent versions, it might just not set the header.
    assert "access-control-allow-origin" not in response.headers


def test_security_headers_present():
    """Test that security headers are present in responses."""
    response = client.get("/")
    assert response.status_code == 200

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "geolocation=()" in response.headers["permissions-policy"]
    assert "default-src 'self'" in response.headers["content-security-policy"]


def test_hsts_header_on_https():
    """Test that HSTS header is present only on HTTPS requests."""
    # Simulate HTTPS request
    response = client.get("/", headers={"X-Forwarded-Proto": "https"})
    # Note: TestClient might not fully simulate HTTPS scheme unless base_url is set to https.
    # Let's try setting the scheme directly if possible or rely on middleware logic.

    # Actually, TestClient uses 'http://testserver' by default.
    # We can try to force it by creating a client with base_url.

    https_client = TestClient(app, base_url="https://testserver")
    response = https_client.get("/")
    assert response.status_code == 200
    assert "strict-transport-security" in response.headers
    assert "max-age=31536000" in response.headers["strict-transport-security"]


def test_hsts_header_missing_on_http():
    """Test that HSTS header is missing on HTTP requests."""
    response = client.get("/")
    assert response.status_code == 200
    assert "strict-transport-security" not in response.headers
