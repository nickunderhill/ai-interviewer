import datetime as dt
import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_user_email_unique_constraint_enforced(db_session):
    from app.models.user import User

    user1 = User(email="unique@example.com", hashed_password="hashed")
    db_session.add(user1)
    await db_session.commit()

    user2 = User(email="unique@example.com", hashed_password="hashed2")
    db_session.add(user2)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_user_timestamps_populated_and_timezone_aware(db_session):
    from app.models.user import User

    user = User(email="ts@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.created_at is not None
    assert user.created_at.tzinfo is not None
    assert user.created_at.utcoffset() == dt.timedelta(0)

    assert user.updated_at is not None
    assert user.updated_at.tzinfo is not None
    assert user.updated_at.utcoffset() == dt.timedelta(0)
