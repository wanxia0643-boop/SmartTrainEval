"""add course table

Revision ID: 20260707_0001
Revises: 20260701_0001
Create Date: 2026-07-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260707_0001'
down_revision = '20260701_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'course',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('course_name', sa.String(150), nullable=False, comment='Course name'),
        sa.Column('course_code', sa.String(64), nullable=False, comment='Unique course code'),
        sa.Column('teacher_id', sa.BigInteger(), nullable=False, comment='Teacher user ID'),
        sa.Column('org_id', sa.BigInteger(), nullable=True, comment='Organization ID'),
        sa.Column('category', sa.String(50), nullable=True, comment='Course category'),
        sa.Column('description', sa.Text(), nullable=True, comment='Course description'),
        sa.Column('start_date', sa.DateTime(), nullable=True, comment='Course start date'),
        sa.Column('end_date', sa.DateTime(), nullable=True, comment='Course end date'),
        sa.Column('status', sa.Integer(), nullable=False, server_default='1', comment='Status: 0-disabled 1-active 2-ended'),
        sa.Column('max_students', sa.Integer(), nullable=True, comment='Maximum number of students'),
        sa.Column('credits', sa.Integer(), nullable=True, comment='Course credits'),
        sa.Column('is_deleted', sa.Integer(), nullable=False, server_default='0', comment='Is deleted: 0-no 1-yes'),
        sa.Column('create_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('update_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('course_code'),
        sa.Index('ix_course_teacher_id', 'teacher_id'),
        sa.Index('ix_course_org_id', 'org_id'),
        sa.Index('ix_course_status', 'status'),
    )


def downgrade() -> None:
    op.drop_table('course')
