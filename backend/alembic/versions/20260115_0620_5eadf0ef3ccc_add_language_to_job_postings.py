"""add_language_to_job_postings

Revision ID: 5eadf0ef3ccc
Revises: 00bdc4df1e2f
Create Date: 2026-01-15 06:20:44.762486+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5eadf0ef3ccc"
down_revision: Union[str, None] = "00bdc4df1e2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add language column with default value 'en' for existing rows
    op.add_column(
        "job_postings",
        sa.Column("language", sa.String(length=2), nullable=False, server_default="en"),
    )
    # Add CHECK constraint to ensure only 'en' or 'ua' values
    op.create_check_constraint(
        "job_postings_language_check", "job_postings", "language IN ('en', 'ua')"
    )


def downgrade() -> None:
    # Drop CHECK constraint first
    op.drop_constraint("job_postings_language_check", "job_postings", type_="check")
    # Drop language column
    op.drop_column("job_postings", "language")
