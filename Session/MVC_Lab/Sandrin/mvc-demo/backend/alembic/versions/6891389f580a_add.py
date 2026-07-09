"""add
Revision ID: 6891389f580a
Revises: 3ce1000eb355
Create Date: 2026-06-18 17:18:52.529116
"""
from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision = '6891389f580a'
down_revision = '3ce1000eb355'
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def upgrade() -> None:
    # Step 1 - add the column as nullable so the schema change succeeds.
    op.add_column('users', sa.Column('password_hash', sa.String(length=200), nullable=True))

    # Step 2 - backfill every existing row with a known hash.
    default_hash = pwd_context.hash('password123')
    op.execute(sa.text('UPDATE users SET password_hash = :hash'), {'hash': default_hash})

    # Step 3 - now make the column NOT NULL.
    op.alter_column('users', 'password_hash', nullable=False)


def downgrade() -> None:
    op.drop_column('users', 'password_hash')
