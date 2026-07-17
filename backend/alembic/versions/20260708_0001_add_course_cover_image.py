"""add course cover_image

Revision ID: 20260708_0001
Revises: 20260707_0001
Create Date: 2026-07-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260708_0001'
down_revision = '20260707_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'course',
        sa.Column('cover_image', sa.String(300), nullable=True, comment='Course cover image URL')
    )


def downgrade() -> None:
    op.drop_column('course', 'cover_image')
