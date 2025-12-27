"""
Database connection and session management using SQLAlchemy async.
Provides async engine, session factory, and dependency injection for FastAPI.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=5,  # Minimum number of connections
    max_overflow=15,  # Maximum connections beyond pool_size (total max = 20)
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Check connection health before usage
    connect_args={
        "timeout": 30,  # Connection timeout in seconds
        "command_timeout": 60,  # Command execution timeout
    },
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that provides database sessions to FastAPI routes.

    Usage in FastAPI endpoint:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session for the request

    Ensures:
        - Session is properly closed after request
        - Connections are returned to the pool
        - Errors are handled gracefully
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions outside of FastAPI request context.

    Usage in background tasks:
        async with get_db_context() as db:
            # Use db here
            ...

    Yields:
        AsyncSession: Database session

    Ensures:
        - Session is properly closed after use
        - Transactions are rolled back on error
        - Connections are returned to the pool
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database connection on application startup.
    Tests connectivity and logs success/failure.
    """
    from sqlalchemy import text

    try:
        # Test database connection
        async with engine.begin() as conn:
            # Execute simple query to verify connection
            await conn.execute(text("SELECT 1"))

        logger.info("✓ Database connected successfully")
        # Log connection info without credentials
        try:
            url_parts = settings.database_url.split("@")
            if len(url_parts) > 1:
                logger.info(f"✓ Connection URL: {url_parts[1]}")
            else:
                logger.info("✓ Connection URL: [configured]")
        except Exception:
            logger.info("✓ Connection URL: [configured]")
        logger.info("✓ Pool size: 5-20 connections")

    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        raise


async def close_db() -> None:
    """
    Close database connection on application shutdown.
    Ensures all connections are properly closed.
    """
    await engine.dispose()
    logger.info("✓ Database connections closed")
