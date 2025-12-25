"""
Tests for SessionMessage model.
"""

import datetime as dt
import uuid as uuid_module

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_session_message_creation_with_session_relationship(db_session):
    """Test SessionMessage creation with session relationship."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage
    from app.models.user import User

    # Create user and session
    user = User(email="message_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create message
    message = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="What is your experience with Python?",
        question_type="technical",
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    assert message.id is not None
    assert isinstance(message.id, uuid_module.UUID)
    assert message.session_id == session.id
    assert message.message_type == "question"
    assert message.content == "What is your experience with Python?"
    assert message.question_type == "technical"


@pytest.mark.asyncio
async def test_session_message_type_field_validation(db_session):
    """Test message_type field accepts both question and answer."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage
    from app.models.user import User

    user = User(email="type_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Test question type
    question = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="Test question?",
        question_type="technical",
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    assert question.message_type == "question"

    # Test answer type
    answer = SessionMessage(
        session_id=session.id,
        message_type="answer",
        content="Test answer",
        question_type=None,
    )
    db_session.add(answer)
    await db_session.commit()
    await db_session.refresh(answer)
    assert answer.message_type == "answer"


@pytest.mark.asyncio
async def test_session_message_content_accepts_large_text(db_session):
    """Test that content field accepts large text (answers can be long)."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage
    from app.models.user import User

    user = User(email="large_text@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create large content (simulate detailed answer)
    large_content = "This is a detailed answer. " * 1000  # ~27KB
    message = SessionMessage(
        session_id=session.id,
        message_type="answer",
        content=large_content,
        question_type=None,
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    assert len(message.content) == len(large_content)
    assert message.content == large_content


@pytest.mark.asyncio
async def test_session_message_question_type_is_nullable(db_session):
    """Test that question_type can be NULL (for answer messages)."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage
    from app.models.user import User

    user = User(email="nullable_type@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    message = SessionMessage(
        session_id=session.id,
        message_type="answer",
        content="Test answer without question_type",
        question_type=None,
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    assert message.question_type is None


@pytest.mark.asyncio
async def test_session_message_ordering_by_created_at(db_session):
    """Test that messages can be ordered by created_at."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage
    from app.models.user import User

    user = User(email="ordering_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create multiple messages
    message1 = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="First question",
        question_type="technical",
    )
    db_session.add(message1)
    await db_session.commit()
    await db_session.refresh(message1)

    message2 = SessionMessage(
        session_id=session.id,
        message_type="answer",
        content="First answer",
        question_type=None,
    )
    db_session.add(message2)
    await db_session.commit()
    await db_session.refresh(message2)

    message3 = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="Second question",
        question_type="behavioral",
    )
    db_session.add(message3)
    await db_session.commit()
    await db_session.refresh(message3)

    # Query messages ordered by created_at
    result = await db_session.execute(
        select(SessionMessage)
        .where(SessionMessage.session_id == session.id)
        .order_by(SessionMessage.created_at)
    )
    messages = result.scalars().all()

    assert len(messages) == 3
    assert messages[0].content == "First question"
    assert messages[1].content == "First answer"
    assert messages[2].content == "Second question"
    # Verify chronological order
    assert messages[0].created_at <= messages[1].created_at
    assert messages[1].created_at <= messages[2].created_at


@pytest.mark.asyncio
async def test_session_message_cascade_on_session_deletion(db_session):
    """Test that deleting session cascades to delete messages."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage
    from app.models.user import User

    user = User(email="cascade_msg@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    message = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="Test question",
        question_type="technical",
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    message_id = message.id

    # Delete session
    await db_session.delete(session)
    await db_session.commit()

    # Verify message was also deleted
    result = await db_session.execute(
        select(SessionMessage).where(SessionMessage.id == message_id)
    )
    deleted_message = result.scalar_one_or_none()
    assert deleted_message is None


@pytest.mark.asyncio
async def test_session_message_timestamps_are_utc_aware(db_session):
    """Test that created_at timestamp is UTC-aware."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage
    from app.models.user import User

    user = User(email="ts_msg@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    message = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="Test",
        question_type="technical",
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    assert message.created_at is not None
    assert message.created_at.tzinfo is not None
    assert message.created_at.utcoffset() == dt.timedelta(0)


@pytest.mark.asyncio
async def test_session_message_session_id_required(db_session):
    """Test that session_id is required (NOT NULL)."""
    from app.models.session_message import SessionMessage

    message = SessionMessage(
        session_id=None,
        message_type="question",
        content="Test question",
        question_type="technical",
    )
    db_session.add(message)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_session_message_relationship_with_session(db_session):
    """Test that message has working relationship with session."""
    from app.models.interview_session import InterviewSession
    from app.models.session_message import SessionMessage
    from app.models.user import User

    user = User(email="rel_msg@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    message = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="Test",
        question_type="technical",
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    # Test forward relationship
    assert message.session is not None
    assert message.session.id == session.id

    # Test back-populate relationship
    await db_session.refresh(session)
    assert len(session.messages) == 1
    assert session.messages[0].id == message.id
