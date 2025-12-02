"""Rename hashed_password to password_hash

Revision ID: 002
Revises: 001
Create Date: 2025-11-30 22:20:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # Rename column from hashed_password to password_hash
    op.alter_column("users", "hashed_password", new_column_name="password_hash")


def downgrade():
    # Rename column back from password_hash to hashed_password
    op.alter_column("users", "password_hash", new_column_name="hashed_password")
