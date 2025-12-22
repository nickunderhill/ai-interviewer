"""
Pytest configuration and fixtures for testing.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
import os
import uuid

from httpx import AsyncClient
import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Ensure security settings are available during tests even if the developer
# hasn't exported them in the shell running pytest.
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DB_HOST", "localhost")
# Generate a valid Fernet key for testing encryption
from cryptography.fernet import Fernet

os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    Uses test database from environment variables.
    """
    # Use test database URL
    test_database_url = (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

    schema_name = f"test_{uuid.uuid4().hex}"

    engine = create_async_engine(
        test_database_url,
        echo=False,
        connect_args={"server_settings": {"search_path": schema_name}},
    )

    # Import models so they're registered with Base.metadata
    from app.models import user as _user  # noqa: F401
    from app.models import resume as _resume  # noqa: F401
    from app.models import job_posting as _job_posting  # noqa: F401

    # Create isolated schema + tables (prevents dropping dev DB objects)
    async with engine.begin() as conn:
        await conn.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        await conn.execute(sa.text(f'SET search_path TO "{schema_name}"'))
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # Cleanup: drop the isolated schema and everything created in it
    async with engine.begin() as conn:
        await conn.execute(sa.text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))

    await engine.dispose()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency to use test database."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test HTTP client with database override."""
    # Add test protected endpoint for auth dependency testing
    from tests.api.v1.test_auth_dependency import create_test_protected_endpoint

    create_test_protected_endpoint(app)

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture
def client(override_get_db) -> Generator:
    """Create synchronous test HTTP client with database override."""
    from fastapi.testclient import TestClient

    # Add test protected endpoint for auth dependency testing
    from tests.api.v1.test_auth_dependency import create_test_protected_endpoint

    create_test_protected_endpoint(app)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user in the database."""
    from app.models.user import User
    from app.core.security import hash_password

    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> dict[str, str]:
    """Create authentication headers with valid JWT token for test user."""
    from app.core.security import create_access_token

    token = create_access_token({"user_id": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
