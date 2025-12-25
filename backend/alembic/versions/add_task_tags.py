"""Add Tags column to Tasks

Revision ID: add_task_tags
Revises: make_task_state_nullable
Create Date: 2025-12-25 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_task_tags"
down_revision: Union[str, Sequence[str], None] = "make_task_state_nullable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add Tags column with default empty string
    op.add_column(
        "Tasks",
        sa.Column("Tags", sa.String(length=512), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("Tasks", "Tags")
