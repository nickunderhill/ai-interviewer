import pytest

from app.core.security import decode_access_token


@pytest.mark.asyncio
async def test_successful_login_returns_bearer_token(client, override_get_db):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "p@ssw0rd!!"},
    )
    assert register.status_code == 201
    user_id = register.json()["id"]

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "p@ssw0rd!!"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]

    payload = decode_access_token(data["access_token"])
    assert payload["user_id"] == user_id


@pytest.mark.asyncio
async def test_wrong_password_returns_401(client, override_get_db):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@example.com", "password": "p@ssw0rd!!"},
    )
    assert register.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "wrongpass!!"},
    )

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_short_wrong_password_returns_401_not_422(client, override_get_db):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "shortpw@example.com", "password": "p@ssw0rd!!"},
    )
    assert register.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "shortpw@example.com", "password": "x"},
    )

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_unknown_email_returns_401(client, override_get_db):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "p@ssw0rd!!"},
    )

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_CREDENTIALS"
