"""drop home_dirs table

Revision ID: 002
Revises: 001
Create Date: 2026-07-27

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("home_dirs")


def downgrade() -> None:
    op.create_table(
        "home_dirs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(255), nullable=False, unique=True),
        sa.Column("dir_id", sa.String(255), nullable=False),
    )
