"""add login token column

Revision ID: a1b2c3d4e5f6
Revises: 6891389f580a
Create Date: 2026-06-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '6891389f580a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('last_login_token', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_login_token')
