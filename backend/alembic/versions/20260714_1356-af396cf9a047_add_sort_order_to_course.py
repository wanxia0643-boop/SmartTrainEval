"""add_sort_order_to_course

Revision ID: af396cf9a047
Revises: 35fd77e55fea
Create Date: 2026-07-14 13:56:19.712523+00:00

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'af396cf9a047'
down_revision: str | None = '35fd77e55fea'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('course', sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0', comment='Sort order (smaller = higher priority, pinned=-1)'))


def downgrade() -> None:
    op.drop_column('course', 'sort_order')
