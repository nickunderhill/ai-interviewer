"""Add retake tracking to interview_sessions

Revision ID: e856d687d853
Revises: 127d39341e56
Create Date: 2025-12-26 05:22:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e856d687d853"
down_revision: Union[str, None] = "127d39341e56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add retake_number column with default value
    op.add_column(
        "interview_sessions",
        sa.Column("retake_number", sa.Integer(), nullable=False, server_default="1"),
    )

    # Add original_session_id column (nullable for first attempts)
    op.add_column(
        "interview_sessions",
        sa.Column("original_session_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Add foreign key constraint for self-referential relationship
    op.create_foreign_key(
        "fk_interview_sessions_original_session_id",
        "interview_sessions",
        "interview_sessions",
        ["original_session_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Add index on original_session_id for query performance
    op.create_index(
        "ix_interview_sessions_original_session_id",
        "interview_sessions",
        ["original_session_id"],
    )


def downgrade() -> None:
    # Drop index
    op.drop_index(
        "ix_interview_sessions_original_session_id", table_name="interview_sessions"
    )

    # Drop foreign key constraint
    op.drop_constraint(
        "fk_interview_sessions_original_session_id",
        "interview_sessions",
        type_="foreignkey",
    )

    # Drop columns
    op.drop_column("interview_sessions", "original_session_id")
    op.drop_column("interview_sessions", "retake_number")
