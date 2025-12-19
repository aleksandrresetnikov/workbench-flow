"""Add project roles and marks, refactor project member role to access level

Revision ID: add_project_roles_and_marks
Revises: add_otp_func
Create Date: 2025-12-18 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_project_roles_and_marks"
down_revision: Union[str, Sequence[str], None] = "add_otp_func"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ProjectRoles table
    op.create_table(
        "ProjectRoles",
        sa.Column("Id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ProjectId", sa.Integer(), sa.ForeignKey("Projects.Id", ondelete="CASCADE"), nullable=False),
        sa.Column("RoleName", sa.String(length=96), nullable=False),
        sa.Column("CreateDate", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("Rate", sa.Integer(), nullable=True),
    )

    # Create Marks table
    op.create_table(
        "Marks",
        sa.Column("Id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("TargetTask", sa.Integer(), sa.ForeignKey("Tasks.Id", ondelete="CASCADE"), nullable=False),
        sa.Column("MarkedById", sa.Integer(), sa.ForeignKey("Users.Id", ondelete="CASCADE"), nullable=False),
        sa.Column("Description", sa.Text(), nullable=False),
        sa.Column("Rate", sa.Integer(), nullable=True),
        sa.Column("CreateDate", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('"Rate" >= 0 AND "Rate" <= 10', name="ValidRates"),
    )

    # Refactor ProjectMembers: add AccessLevel and RoleId, migrate data from Role and drop Role
    # 1) Add new columns
    op.add_column(
        "ProjectMembers",
        sa.Column("AccessLevel", sa.String(length=10), nullable=False, server_default="Common"),
    )
    op.add_column(
        "ProjectMembers",
        sa.Column("RoleId", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "ProjectMembers_RoleId_fkey",
        "ProjectMembers",
        "ProjectRoles",
        ["RoleId"],
        ["Id"],
        ondelete="SET NULL",
    )

    # 2) Copy old Role into AccessLevel if Role column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("ProjectMembers")]
    if "Role" in columns:
        conn.execute(
            sa.text('UPDATE "ProjectMembers" SET "AccessLevel" = COALESCE("Role", \'Common\')')
        )

    # 3) Drop old constraint and column Role if present
    constraints = inspector.get_check_constraints("ProjectMembers")
    for c in constraints:
        if c["name"] == "ValidRoles":
            op.drop_constraint("ValidRoles", "ProjectMembers", type_="check")
            break

    if "Role" in columns:
        op.drop_column("ProjectMembers", "Role")

    # 4) Add new check constraint for AccessLevel
    op.create_check_constraint(
        "ValidAccessLevels",
        "ProjectMembers",
        '"AccessLevel" IN (\'Common\', \'Admin\')',
    )

    # Remove server_default from AccessLevel
    op.alter_column("ProjectMembers", "AccessLevel", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    # Restore Role column on ProjectMembers (best-effort)
    op.add_column(
        "ProjectMembers",
        sa.Column("Role", sa.String(length=6), nullable=False, server_default="Common"),
    )
    # Migrate AccessLevel back into Role
    conn = op.get_bind()
    conn.execute(
        sa.text('UPDATE "ProjectMembers" SET "Role" = COALESCE("AccessLevel", \'Common\')')
    )
    op.create_check_constraint(
        "ValidRoles",
        "ProjectMembers",
        '"Role" IN (\'Common\', \'Admin\')',
    )

    # Drop new constraint and columns
    op.drop_constraint("ValidAccessLevels", "ProjectMembers", type_="check")
    op.drop_constraint("ProjectMembers_RoleId_fkey", "ProjectMembers", type_="foreignkey")
    op.drop_column("ProjectMembers", "RoleId")
    op.drop_column("ProjectMembers", "AccessLevel")

    # Drop Marks table
    op.drop_table("Marks")

    # Drop ProjectRoles table
    op.drop_table("ProjectRoles")


