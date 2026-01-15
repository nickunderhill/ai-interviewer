"""
Job Posting model for storing job descriptions users want to practice for.
"""

import datetime as dt
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession
    from app.models.user import User


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class JobPosting(Base):
    """JobPosting model - stores job postings for interview practice."""

    __tablename__ = "job_postings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Index for query performance
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    experience_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    tech_stack: Mapped[list[str] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    language: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="en",
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

    # Relationship to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="job_postings",
    )

    # Relationship to InterviewSessions (one-to-many)
    interview_sessions: Mapped[list["InterviewSession"]] = relationship(
        "InterviewSession",
        back_populates="job_posting",
    )

    # Composite index for efficient ordering by created_at within user
    __table_args__ = (
        Index(
            "ix_job_postings_user_id_created_at",
            "user_id",
            "created_at",
        ),
    )
