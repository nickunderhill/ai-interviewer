import pytest
from fastapi import Depends, FastAPI
from httpx import AsyncClient

from app.api.deps import get_token_payload


@pytest.mark.asyncio
async def test_token_payload_dependency_accepts_bearer_token(client, override_get_db):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "dep@example.com", "password": "p@ssw0rd!!"},
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "dep@example.com", "password": "p@ssw0rd!!"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    app = FastAPI()

    @app.get("/protected")
    async def protected(payload=Depends(get_token_payload)):
        return {"user_id": payload["user_id"]}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resp.status_code == 200
    assert resp.json()["user_id"]
