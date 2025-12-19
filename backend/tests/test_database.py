"""
Unit tests for database configuration and connection.
Tests SQLAlchemy async engine, session factory, and dependencies.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import (
    AsyncSessionLocal,
    Base,
    close_db,
    engine,
    get_db,
    init_db,
)


class TestDatabaseConfiguration:
    """Test database configuration settings."""

    def test_database_url_format(self):
        """Test that database URL is correctly formatted for async PostgreSQL."""
        assert settings.database_url.startswith("postgresql+asyncpg://")
        assert "ai_interviewer_db" in settings.database_url
        assert "ai_interviewer_user" in settings.database_url

    def test_database_url_sync_format(self):
        """Test that sync database URL is correctly formatted (for Alembic)."""
        assert settings.database_url_sync.startswith("postgresql://")
        assert "ai_interviewer_db" in settings.database_url_sync
        assert "ai_interviewer_user" in settings.database_url_sync
        # Sync URL should NOT have +asyncpg driver
        assert "+asyncpg" not in settings.database_url_sync

    def test_settings_loaded_from_env(self):
        """Test that settings are properly loaded from .env file."""
        assert settings.DB_HOST is not None
        assert settings.DB_PORT == 5432
        assert settings.DB_NAME == "ai_interviewer_db"
        assert settings.DB_USER == "ai_interviewer_user"
        assert settings.DB_PASSWORD is not None


class TestDatabaseEngine:
    """Test SQLAlchemy async engine configuration."""

    def test_engine_exists(self):
        """Test that async engine is created."""
        assert engine is not None

    def test_engine_pool_configuration(self):
        """Test that connection pool is configured correctly."""
        # Pool size should be 5
        assert engine.pool.size() == 5
        # Max overflow should be 15 (total max = 20)
        assert engine.pool._max_overflow == 15

    def test_engine_url(self):
        """Test that engine uses correct async PostgreSQL URL."""
        assert "postgresql+asyncpg" in str(engine.url)


class TestSessionFactory:
    """Test async session factory."""

    def test_session_factory_exists(self):
        """Test that AsyncSessionLocal is created."""
        assert AsyncSessionLocal is not None

    @pytest.mark.asyncio
    async def test_session_factory_creates_sessions(self):
        """Test that session factory creates valid async sessions."""
        async with AsyncSessionLocal() as session:
            assert isinstance(session, AsyncSession)
            assert not session.is_active  # No transaction until first query

    @pytest.mark.asyncio
    async def test_session_execute_query(self):
        """Test that session can execute queries."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1 as num"))
            row = result.fetchone()
            assert row[0] == 1


class TestGetDbDependency:
    """Test get_db dependency function."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test that get_db yields a valid AsyncSession."""
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            break  # Only test first yield

    @pytest.mark.asyncio
    async def test_get_db_closes_session(self):
        """Test that get_db properly closes session after use."""
        async for session in get_db():
            # Simulate using the session
            await session.execute(text("SELECT 1"))
            break

        # After context exit, session should be closed
        # Note: We can't directly test this without internal access,
        # but we verify no exception is raised

    @pytest.mark.asyncio
    async def test_get_db_multiple_calls(self):
        """Test that get_db can be called multiple times (connection pooling)."""
        sessions = []
        for _ in range(3):
            async for session in get_db():
                sessions.append(session)
                await session.execute(text("SELECT 1"))
                break

        # Should have created 3 sessions
        assert len(sessions) == 3


class TestDatabaseInitialization:
    """Test database initialization and lifecycle."""

    @pytest.mark.asyncio
    async def test_init_db_success(self):
        """Test that init_db successfully connects to database."""
        # Should not raise exception
        await init_db()

    @pytest.mark.asyncio
    async def test_close_db_success(self):
        """Test that close_db properly disposes engine."""
        # Ensure init first
        await init_db()
        # Should not raise exception
        await close_db()
        # Re-initialize for other tests
        await init_db()


class TestBaseModel:
    """Test declarative base for ORM models."""

    def test_base_exists(self):
        """Test that Base declarative class exists."""
        assert Base is not None

    def test_base_metadata(self):
        """Test that Base has metadata attribute."""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None


class TestDatabaseConnectivity:
    """Integration tests for actual database connectivity."""

    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test that we can connect to the database."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            # Should return PostgreSQL version string
            assert "PostgreSQL" in version

    @pytest.mark.asyncio
    async def test_database_current_database(self):
        """Test that we're connected to the correct database."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            assert db_name == "ai_interviewer_db"

    @pytest.mark.asyncio
    async def test_database_current_user(self):
        """Test that we're connected with the correct user."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT current_user"))
            user = result.scalar()
            assert user == "ai_interviewer_user"

    @pytest.mark.asyncio
    async def test_connection_pool_usage(self):
        """Test that connection pool handles concurrent sessions."""

        async def execute_query():
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))

        # Execute multiple queries concurrently (simulating concurrent requests)
        import asyncio

        tasks = [execute_query() for _ in range(10)]
        await asyncio.gather(*tasks)
        # Should complete without errors, demonstrating connection pooling

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """Test that transactions can be rolled back."""
        async with AsyncSessionLocal() as session:
            # Start a transaction
            await session.execute(text("SELECT 1"))
            # Rollback (session closes automatically, rolling back uncommitted work)
            await session.rollback()
        # Should not raise exception

    @pytest.mark.asyncio
    async def test_session_isolation(self):
        """Test that sessions are isolated from each other."""
        # Create two separate sessions
        async with AsyncSessionLocal() as session1, AsyncSessionLocal() as session2:
            # Both should work independently
            result1 = await session1.execute(text("SELECT 1 as val"))
            result2 = await session2.execute(text("SELECT 2 as val"))

            assert result1.scalar() == 1
            assert result2.scalar() == 2
