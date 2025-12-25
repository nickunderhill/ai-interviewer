"""Tests for InterviewFeedback model."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview_feedback import InterviewFeedback


def test_interview_feedback_tablename():
    """InterviewFeedback must follow plural_snake_case naming."""
    from app.models.interview_feedback import InterviewFeedback

    assert InterviewFeedback.__tablename__ == "interview_feedbacks"


@pytest.mark.asyncio
async def test_one_to_one_constraint_prevents_duplicate_feedback(
    db_session: AsyncSession,
):
    """Test that unique constraint on session_id prevents multiple feedback records for same session."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    # Create user and session
    user = User(email="test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        status="completed",
        current_question_number=5,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create first feedback
    feedback1 = InterviewFeedback(
        session_id=session.id,
        technical_accuracy_score=85,
        communication_clarity_score=80,
        problem_solving_score=90,
        relevance_score=88,
        overall_score=86,
        technical_feedback="Strong technical knowledge",
        communication_feedback="Clear communication",
        problem_solving_feedback="Good problem-solving approach",
        relevance_feedback="Relevant answers",
        overall_comments="Good overall performance",
        knowledge_gaps=["React hooks", "TypeScript generics"],
        learning_recommendations=["Study async patterns", "Practice system design"],
    )
    db_session.add(feedback1)
    await db_session.commit()
    await db_session.refresh(feedback1)

    # Attempt to create second feedback for same session
    feedback2 = InterviewFeedback(
        session_id=session.id,
        technical_accuracy_score=75,
        communication_clarity_score=70,
        problem_solving_score=80,
        relevance_score=78,
        overall_score=76,
        technical_feedback="Different feedback",
        communication_feedback="Different feedback",
        problem_solving_feedback="Different feedback",
        relevance_feedback="Different feedback",
        knowledge_gaps=[],
        learning_recommendations=[],
    )
    db_session.add(feedback2)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_json_array_fields_round_trip(db_session: AsyncSession):
    """Test that knowledge_gaps and learning_recommendations store and retrieve lists correctly."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="json_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        status="completed",
        current_question_number=3,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create feedback with JSON arrays
    knowledge_gaps_data = [
        "Algorithm optimization",
        "Database indexing",
        "Caching strategies",
    ]
    learning_recs_data = [
        "Review data structures",
        "Study distributed systems",
        "Practice coding challenges",
    ]

    feedback = InterviewFeedback(
        session_id=session.id,
        technical_accuracy_score=80,
        communication_clarity_score=75,
        problem_solving_score=85,
        relevance_score=82,
        overall_score=81,
        technical_feedback="Good technical skills",
        communication_feedback="Could improve clarity",
        problem_solving_feedback="Strong problem solver",
        relevance_feedback="Mostly relevant",
        knowledge_gaps=knowledge_gaps_data,
        learning_recommendations=learning_recs_data,
    )
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(feedback)

    # Verify data round-trips correctly
    assert feedback.knowledge_gaps == knowledge_gaps_data
    assert feedback.learning_recommendations == learning_recs_data
    assert isinstance(feedback.knowledge_gaps, list)
    assert isinstance(feedback.learning_recommendations, list)
    assert len(feedback.knowledge_gaps) == 3
    assert len(feedback.learning_recommendations) == 3


@pytest.mark.asyncio
async def test_timestamps_are_utc_aware(db_session: AsyncSession):
    """Test that created_at and updated_at are UTC-aware."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="timestamp_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        status="completed",
        current_question_number=2,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    feedback = InterviewFeedback(
        session_id=session.id,
        technical_accuracy_score=90,
        communication_clarity_score=88,
        problem_solving_score=92,
        relevance_score=89,
        overall_score=90,
        technical_feedback="Excellent",
        communication_feedback="Very clear",
        problem_solving_feedback="Outstanding",
        relevance_feedback="Highly relevant",
        knowledge_gaps=[],
        learning_recommendations=[],
    )
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(feedback)

    # Verify timestamps are UTC-aware
    assert feedback.created_at.tzinfo is not None
    assert feedback.updated_at.tzinfo is not None
    # UTC offset should be 0
    assert feedback.created_at.utcoffset().total_seconds() == 0
    assert feedback.updated_at.utcoffset().total_seconds() == 0


@pytest.mark.asyncio
async def test_feedback_cascade_deletes_with_session(db_session: AsyncSession):
    """Test that deleting session cascades to delete feedback."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="cascade_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        status="completed",
        current_question_number=4,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    feedback = InterviewFeedback(
        session_id=session.id,
        technical_accuracy_score=85,
        communication_clarity_score=80,
        problem_solving_score=88,
        relevance_score=86,
        overall_score=85,
        technical_feedback="Good",
        communication_feedback="Clear",
        problem_solving_feedback="Strong",
        relevance_feedback="Relevant",
        knowledge_gaps=["Testing strategies"],
        learning_recommendations=["Practice TDD"],
    )
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(feedback)

    feedback_id = feedback.id

    # Delete session
    await db_session.delete(session)
    await db_session.commit()

    # Verify feedback was also deleted
    result = await db_session.execute(
        select(InterviewFeedback).where(InterviewFeedback.id == feedback_id)
    )
    deleted_feedback = result.scalar_one_or_none()
    assert deleted_feedback is None


@pytest.mark.asyncio
async def test_feedback_empty_json_arrays(db_session: AsyncSession):
    """Test that empty arrays work correctly for JSON fields."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="empty_json@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        status="completed",
        current_question_number=1,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    feedback = InterviewFeedback(
        session_id=session.id,
        technical_accuracy_score=95,
        communication_clarity_score=92,
        problem_solving_score=96,
        relevance_score=94,
        overall_score=94,
        technical_feedback="Perfect technical execution",
        communication_feedback="Excellent communication",
        problem_solving_feedback="Creative solutions",
        relevance_feedback="Perfectly on topic",
        knowledge_gaps=[],
        learning_recommendations=[],
    )
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(feedback)

    assert feedback.knowledge_gaps == []
    assert feedback.learning_recommendations == []
    assert isinstance(feedback.knowledge_gaps, list)
    assert isinstance(feedback.learning_recommendations, list)


@pytest.mark.asyncio
async def test_feedback_relationship_accessible_from_session(db_session: AsyncSession):
    """Test that feedback can be accessed via session.feedback relationship."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="relationship@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        status="completed",
        current_question_number=6,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    feedback = InterviewFeedback(
        session_id=session.id,
        technical_accuracy_score=88,
        communication_clarity_score=85,
        problem_solving_score=90,
        relevance_score=87,
        overall_score=88,
        technical_feedback="Strong",
        communication_feedback="Good",
        problem_solving_feedback="Excellent",
        relevance_feedback="On point",
        knowledge_gaps=["Advanced patterns"],
        learning_recommendations=["Study design patterns"],
    )
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(session)

    # Access feedback via session relationship
    assert session.feedback is not None
    assert session.feedback.id == feedback.id
    assert session.feedback.overall_score == 88


def test_interview_session_has_feedback_relationship():
    """InterviewSession must expose a one-to-one feedback relationship."""
    from app.models.interview_session import InterviewSession

    assert hasattr(InterviewSession, "feedback")
