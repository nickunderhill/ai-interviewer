from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.dependencies import get_current_user

client = TestClient(app)


def test_register_rejects_invalid_email() -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )
    assert response.status_code == 422


def test_register_rejects_oversized_password() -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "a" * 1000},
    )
    assert response.status_code == 422


def test_sessions_rejects_invalid_status_enum() -> None:
    async def override_get_db():
        yield None

    def override_get_current_user():
        class DummyUser:
            id = "00000000-0000-0000-0000-000000000000"

        return DummyUser()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        response = client.get("/api/v1/sessions", params={"status": "bogus"})
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
