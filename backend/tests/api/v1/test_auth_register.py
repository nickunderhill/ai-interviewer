import uuid

import pytest
from sqlalchemy import select

from app.models.user import User


@pytest.mark.asyncio
async def test_successful_registration(client, override_get_db):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "p@ssw0rd!!"},
    )

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data
    assert uuid.UUID(data["id"])  # valid UUID
    assert "created_at" in data


@pytest.mark.asyncio
async def test_duplicate_email_returns_409(client, override_get_db):
    first = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "p@ssw0rd!!"},
    )
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "p@ssw0rd!!"},
    )

    assert second.status_code == 409
    detail = second.json()["detail"]
    assert detail["code"] == "EMAIL_ALREADY_REGISTERED"


@pytest.mark.asyncio
async def test_invalid_email_returns_422(client, override_get_db):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "p@ssw0rd!!"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_password_is_hashed_in_database(client, override_get_db, db_session):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "hashme@example.com", "password": "p@ssw0rd!!"},
    )
    assert response.status_code == 201

    result = await db_session.execute(
        select(User).where(User.email == "hashme@example.com")
    )
    user = result.scalar_one()

    assert user.hashed_password != "p@ssw0rd!!"
    assert user.hashed_password.startswith("$2")
    assert "$12$" in user.hashed_password


@pytest.mark.asyncio
async def test_email_is_normalized_and_case_insensitive_duplicate_returns_409(
    client, override_get_db
):
    first = await client.post(
        "/api/v1/auth/register",
        json={"email": "User@Example.com", "password": "p@ssw0rd!!"},
    )
    assert first.status_code == 201
    assert first.json()["email"] == "user@example.com"

    second = await client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "p@ssw0rd!!"},
    )
    assert second.status_code == 409
    detail = second.json()["detail"]
    assert detail["code"] == "EMAIL_ALREADY_REGISTERED"
