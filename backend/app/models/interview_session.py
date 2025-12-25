"""
InterviewSession model for tracking AI-powered interview sessions.
"""

import datetime as dt
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_posting import JobPosting
    from app.models.session_message import SessionMessage
    from app.models.interview_feedback import InterviewFeedback
    from app.models.interview_feedback import InterviewFeedback


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


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

    job_posting_id: Mapped[Optional[uuid.UUID]] = mapped_column(
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

    messages: Mapped[List["SessionMessage"]] = relationship(
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

    feedback: Mapped[Optional["InterviewFeedback"]] = relationship(
        "InterviewFeedback",
        back_populates="session",
        uselist=False,
        lazy="selectin",
    )

    # Composite index for efficient queries
    __table_args__ = (
        Index(
            "ix_interview_sessions_user_id_created_at",
            "user_id",
            "created_at",
        ),
    )
