"""Operation model for tracking long-running async operations."""

import datetime as dt
import uuid
from typing import Optional

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utcnow() -> dt.datetime:
    """Return current UTC datetime."""
    return dt.datetime.now(dt.timezone.utc)


class Operation(Base):
    """Operation model - tracks long-running async operations.

    Supports tracking operations like question generation and feedback
    analysis with JSON results and error handling.
    """

    __tablename__ = "operations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    operation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    result: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
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

    __table_args__ = (
        Index(
            "ix_operations_type_status",
            "operation_type",
            "status",
        ),
    )
