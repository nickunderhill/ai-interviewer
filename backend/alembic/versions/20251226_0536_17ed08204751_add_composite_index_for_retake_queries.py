"""Add composite index for retake queries

Revision ID: 17ed08204751
Revises: e856d687d853
Create Date: 2025-12-26 05:36:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "17ed08204751"
down_revision: Union[str, None] = "e856d687d853"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add composite index for efficient retake chain queries
    # Query pattern: "Get all attempts for this job by this user"
    op.create_index(
        "ix_interview_sessions_user_job_original",
        "interview_sessions",
        ["user_id", "job_posting_id", "original_session_id"],
    )


def downgrade() -> None:
    # Drop composite index
    op.drop_index(
        "ix_interview_sessions_user_job_original", table_name="interview_sessions"
    )
