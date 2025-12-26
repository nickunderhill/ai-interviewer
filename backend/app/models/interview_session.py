"""
InterviewSession model for tracking AI-powered interview sessions.
"""

import datetime as dt
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.interview_feedback import InterviewFeedback
    from app.models.job_posting import JobPosting
    from app.models.session_message import SessionMessage
    from app.models.user import User


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class InterviewSession(Base):
    """InterviewSession model - tracks AI-powered interview sessions."""

    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_posting_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_postings.id", ondelete="SET NULL"),
        nullable=True,  # Nullable to preserve session if job posting deleted
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    current_question_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    retake_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    original_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
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

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="interview_sessions",
    )

    job_posting: Mapped[Optional["JobPosting"]] = relationship(
        "JobPosting",
        back_populates="interview_sessions",
    )

    messages: Mapped[list["SessionMessage"]] = relationship(
        "SessionMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionMessage.created_at",
        lazy="selectin",
    )

    feedback: Mapped[Optional["InterviewFeedback"]] = relationship(
        "InterviewFeedback",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Self-referential relationship for retake tracking
    # Note: ondelete="SET NULL" preserves retake sessions when original is deleted
    # This allows retakes to persist as standalone sessions while losing the link
    original_session: Mapped[Optional["InterviewSession"]] = relationship(
        "InterviewSession",
        remote_side=[id],  # Specifies which side is the "parent" in self-reference
        back_populates="retakes",
        foreign_keys=[original_session_id],
        lazy="selectin",
    )

    retakes: Mapped[list["InterviewSession"]] = relationship(
        "InterviewSession",
        back_populates="original_session",
        foreign_keys=[
            original_session_id
        ],  # Explicit FK for bidirectional self-reference
        lazy="selectin",
    )

    # Composite indexes for efficient queries
    __table_args__ = (
        Index(
            "ix_interview_sessions_user_id_created_at",
            "user_id",
            "created_at",
        ),
        # Index for retake chain queries: "all attempts at this job by this user"
        Index(
            "ix_interview_sessions_user_job_original",
            "user_id",
            "job_posting_id",
            "original_session_id",
        ),
    )
