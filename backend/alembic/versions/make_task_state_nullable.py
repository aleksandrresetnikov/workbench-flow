"""Make Tasks.StateId nullable and remove default 0

Revision ID: make_task_state_nullable
Revises: add_project_roles_and_marks
Create Date: 2025-12-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "make_task_state_nullable"
down_revision: Union[str, Sequence[str], None] = "add_project_roles_and_marks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make StateId nullable and remove server default 0
    op.alter_column(
        "Tasks",
        "StateId",
        existing_type=sa.Integer(),
        nullable=True,
        server_default=None,
    )


def downgrade() -> None:
    # Revert to NOT NULL and server default 0 (best-effort)
    op.alter_column(
        "Tasks",
        "StateId",
        existing_type=sa.Integer(),
        nullable=False,
        server_default=sa.text("0"),
    )
