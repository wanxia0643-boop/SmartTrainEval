"""add enterprise mentor assignment to projects

Revision ID: 20260701_0001
Revises:
Create Date: 2026-07-01 00:01:00
"""
from alembic import op
import sqlalchemy as sa


revision = "20260701_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "train_project",
        sa.Column("enterprise_id", sa.BigInteger(), nullable=True, comment="Enterprise mentor user ID"),
    )
    op.create_index("idx_enterprise_id", "train_project", ["enterprise_id"])


def downgrade() -> None:
    op.drop_index("idx_enterprise_id", table_name="train_project")
    op.drop_column("train_project", "enterprise_id")
