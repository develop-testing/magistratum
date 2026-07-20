"""add dirs_to_image table

Revision ID: 001
Revises:
Create Date: 2026-07-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dirs_to_image",
        sa.Column("dir_id", sa.String(255), nullable=False, unique=True),
        sa.Column("image_path", sa.String(500), nullable=False),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("dir_id"),
    )


def downgrade() -> None:
    op.drop_table("dirs_to_image")
