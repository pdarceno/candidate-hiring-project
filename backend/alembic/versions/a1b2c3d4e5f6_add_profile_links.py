"""Add profile_links to candidates

Revision ID: a1b2c3d4e5f6
Revises: 7796b1d63b92
Create Date: 2026-08-11 05:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7796b1d63b92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add profile_links column to candidates table."""
    op.add_column('candidates', sa.Column('profile_links', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    """Remove profile_links column from candidates table."""
    op.drop_column('candidates', 'profile_links')
