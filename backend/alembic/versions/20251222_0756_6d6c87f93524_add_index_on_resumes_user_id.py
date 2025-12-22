"""add index on resumes user_id

Revision ID: 6d6c87f93524
Revises: 130320381949
Create Date: 2025-12-22 07:56:23.092799+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d6c87f93524"
down_revision: Union[str, None] = "130320381949"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: This migration was auto-generated but is empty.
    # The actual index creation is in migration ca77a739011c.
    # This serves as a revision step in the migration chain.
    pass


def downgrade() -> None:
    # NOTE: No-op migration - nothing to downgrade
    pass
