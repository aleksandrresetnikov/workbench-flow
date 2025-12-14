"""Add OTP functionality

Revision ID: add_otp_func
Revises:
Create Date: 2025-12-14 17:29:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_otp_func'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add OtpId column to Users table
    op.add_column('Users', sa.Column('OtpId', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('Users_OtpId_fkey', 'Users', 'Otps', ['OtpId'], ['Id'], ondelete='SET NULL')


def downgrade() -> None:
    """Downgrade schema."""
    # Remove foreign key and column from Users
    op.drop_constraint('Users_OtpId_fkey', 'Users', type_='foreignkey')
    op.drop_column('Users', 'OtpId')