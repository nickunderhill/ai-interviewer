"""add_index_resumes_user_id

Revision ID: ca77a739011c
Revises: 6d6c87f93524
Create Date: 2025-12-22 07:56:30.138144+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ca77a739011c"
down_revision: Union[str, None] = "6d6c87f93524"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create index on resumes.user_id for query performance
    op.create_index(op.f("ix_resumes_user_id"), "resumes", ["user_id"], unique=False)


def downgrade() -> None:
    # Drop index on resumes.user_id
    op.drop_index(op.f("ix_resumes_user_id"), table_name="resumes")
