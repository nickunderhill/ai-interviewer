import datetime as dt
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.job_posting import JobPosting
    from app.models.interview_session import InterviewSession


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    encrypted_api_key: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
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

    # Relationship to Resume (one-to-one)
    resume: Mapped[Optional["Resume"]] = relationship(
        "Resume",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Relationship to JobPostings (one-to-many)
    job_postings: Mapped[List["JobPosting"]] = relationship(
        "JobPosting",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relationship to InterviewSessions (one-to-many)
    interview_sessions: Mapped[List["InterviewSession"]] = relationship(
        "InterviewSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
