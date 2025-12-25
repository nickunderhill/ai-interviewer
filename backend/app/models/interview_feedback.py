"""InterviewFeedback model for AI-generated interview analysis results."""

import datetime as dt
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class InterviewFeedback(Base):
    """InterviewFeedback model - stores AI-generated feedback for a session."""

    __tablename__ = "interview_feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    technical_accuracy_score: Mapped[int] = mapped_column(Integer, nullable=False)
    communication_clarity_score: Mapped[int] = mapped_column(Integer, nullable=False)
    problem_solving_score: Mapped[int] = mapped_column(Integer, nullable=False)
    relevance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)

    technical_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    communication_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    problem_solving_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    overall_comments: Mapped[str | None] = mapped_column(Text, nullable=True)

    knowledge_gaps: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    learning_recommendations: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession",
        back_populates="feedback",
    )
