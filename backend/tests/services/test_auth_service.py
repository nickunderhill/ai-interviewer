import pytest

from app.services.auth_service import authenticate_user
from app.services.user_service import create_user


@pytest.mark.asyncio
async def test_authenticate_user_returns_user_for_valid_credentials(db_session):
    user = await create_user(db_session, email="user@example.com", password="p@ssw0rd!!")

    authenticated = await authenticate_user(db_session, email="user@example.com", password="p@ssw0rd!!")

    assert authenticated is not None
    assert authenticated.id == user.id


@pytest.mark.asyncio
async def test_authenticate_user_returns_none_for_wrong_password(db_session):
    await create_user(db_session, email="user@example.com", password="p@ssw0rd!!")

    authenticated = await authenticate_user(db_session, email="user@example.com", password="wrongpass!!")

    assert authenticated is None


@pytest.mark.asyncio
async def test_authenticate_user_returns_none_for_unknown_email(db_session):
    authenticated = await authenticate_user(db_session, email="missing@example.com", password="p@ssw0rd!!")

    assert authenticated is None
