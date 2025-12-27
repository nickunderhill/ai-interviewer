"""Add retry tracking to operations

Revision ID: 20251227_0200
Revises: 17ed08204751
Create Date: 2025-12-27 02:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20251227_0200"
down_revision: Union[str, None] = "17ed08204751"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add retry_count column with default value 0
    op.add_column(
        "operations",
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
    )

    # Add parent_operation_id column (nullable for initial operations)
    op.add_column(
        "operations",
        sa.Column("parent_operation_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Add foreign key constraint for self-referential relationship
    op.create_foreign_key(
        "fk_operations_parent_operation_id",
        "operations",
        "operations",
        ["parent_operation_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Add index on parent_operation_id for query performance
    op.create_index(
        "ix_operations_parent_operation_id",
        "operations",
        ["parent_operation_id"],
    )


def downgrade() -> None:
    # Remove index first
    op.drop_index("ix_operations_parent_operation_id", table_name="operations")

    # Remove foreign key constraint
    op.drop_constraint(
        "fk_operations_parent_operation_id",
        "operations",
        type_="foreignkey",
    )

    # Remove columns
    op.drop_column("operations", "parent_operation_id")
    op.drop_column("operations", "retry_count")
