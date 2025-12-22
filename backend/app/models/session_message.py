"""
SessionMessage model for storing Q&A messages in interview sessions.
"""

import datetime as dt
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class SessionMessage(Base):
    """SessionMessage model - stores Q&A messages in interview sessions."""

    __tablename__ = "session_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    message_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,  # Only applicable for message_type='question'
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    # Relationships
    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession",
        back_populates="messages",
    )

    # Composite index for efficient message retrieval
    __table_args__ = (
        Index(
            "ix_session_messages_session_id_created_at",
            "session_id",
            "created_at",
        ),
    )
