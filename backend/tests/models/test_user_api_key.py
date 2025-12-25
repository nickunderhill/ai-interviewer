"""
Tests for User model encrypted_api_key field.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_user_model_has_encrypted_api_key_column(
    db_session: AsyncSession,
) -> None:
    """Test that User model has encrypted_api_key column by creating a user with it."""
    from app.core.security import hash_password

    # If we can create and query a user with encrypted_api_key, the column exists
    user = User(
        email="test_column_exists@example.com",
        hashed_password=hash_password("testpass123"),
        encrypted_api_key="test_value",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Column exists if we can access it
    assert hasattr(user, "encrypted_api_key")
    assert user.encrypted_api_key == "test_value"


@pytest.mark.asyncio
async def test_encrypted_api_key_field_is_nullable(
    db_session: AsyncSession,
) -> None:
    """Test that encrypted_api_key can be null."""
    from app.core.security import hash_password

    # Create user without API key
    user = User(
        email="test_nullable@example.com",
        hashed_password=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Verify encrypted_api_key is None
    assert user.encrypted_api_key is None


@pytest.mark.asyncio
async def test_encrypted_api_key_can_store_value(
    db_session: AsyncSession,
) -> None:
    """Test that encrypted_api_key can store encrypted values."""
    from app.core.security import hash_password

    # Create user with API key
    user = User(
        email="test_with_key@example.com",
        hashed_password=hash_password("testpass123"),
        encrypted_api_key="encrypted_value_here",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Verify encrypted_api_key is stored
    assert user.encrypted_api_key == "encrypted_value_here"
