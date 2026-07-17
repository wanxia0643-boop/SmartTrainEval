"""add AI training agent business tables

Revision ID: 20260717_0001
Revises: 0df3fede1576
"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "20260717_0001"
down_revision: str | None = "0df3fede1576"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _common_columns():
    return [
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("create_time", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("update_time", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("is_deleted", sa.SmallInteger(), server_default="0", nullable=False),
    ]


def upgrade() -> None:
    op.add_column("train_project", sa.Column("course_id", sa.BigInteger(), nullable=True, comment="Owning course ID"))
    op.create_index("ix_train_project_course_id", "train_project", ["course_id"])

    op.create_table(
        "work_item",
        *_common_columns(),
        sa.Column("assignee_id", sa.BigInteger(), nullable=False),
        sa.Column("creator_id", sa.BigInteger(), nullable=True),
        sa.Column("task_type", sa.String(40), nullable=False),
        sa.Column("biz_type", sa.String(40), nullable=False),
        sa.Column("biz_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("status", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("due_time", sa.DateTime(), nullable=True),
        sa.Column("resolved_time", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, cols in {
        "ix_work_item_assignee_id": ["assignee_id"],
        "ix_work_item_creator_id": ["creator_id"],
        "ix_work_item_task_type": ["task_type"],
        "ix_work_item_biz_type": ["biz_type"],
        "ix_work_item_biz_id": ["biz_id"],
        "ix_work_item_priority": ["priority"],
        "ix_work_item_status": ["status"],
        "ix_work_item_due_time": ["due_time"],
    }.items():
        op.create_index(name, "work_item", cols)

    op.create_table(
        "knowledge_document",
        *_common_columns(),
        sa.Column("course_id", sa.BigInteger(), nullable=True),
        sa.Column("project_id", sa.BigInteger(), nullable=True),
        sa.Column("uploader_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=True),
        sa.Column("status", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("error_msg", sa.String(1000), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    for col in ("course_id", "project_id", "uploader_id", "status"):
        op.create_index(f"ix_knowledge_document_{col}", "knowledge_document", [col])

    op.create_table(
        "knowledge_chunk",
        *_common_columns(),
        sa.Column("document_id", sa.BigInteger(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("source_label", sa.String(255), nullable=True),
        sa.Column("content", mysql.LONGTEXT(), nullable=False),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_chunk_document_id", "knowledge_chunk", ["document_id"])

    op.create_table(
        "ai_session",
        *_common_columns(),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=True),
        sa.Column("project_id", sa.BigInteger(), nullable=True),
        sa.Column("scene", sa.String(40), nullable=False, server_default="COACH"),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("status", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
    )
    for col in ("user_id", "course_id", "project_id", "scene", "status"):
        op.create_index(f"ix_ai_session_{col}", "ai_session", [col])

    op.create_table(
        "ai_message",
        *_common_columns(),
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", mysql.LONGTEXT(), nullable=False),
        sa.Column("citations_json", mysql.LONGTEXT(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_message_session_id", "ai_message", ["session_id"])

    op.create_table(
        "ai_analysis",
        *_common_columns(),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("scene", sa.String(50), nullable=False),
        sa.Column("biz_type", sa.String(40), nullable=False),
        sa.Column("biz_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("result_json", mysql.LONGTEXT(), nullable=False),
        sa.Column("citations_json", mysql.LONGTEXT(), nullable=True),
        sa.Column("model_name", sa.String(100), nullable=True),
        sa.Column("prompt_version", sa.String(40), nullable=False, server_default="v1"),
        sa.Column("llm_log_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    for col in ("user_id", "scene", "biz_type", "biz_id", "status", "llm_log_id"):
        op.create_index(f"ix_ai_analysis_{col}", "ai_analysis", [col])


def downgrade() -> None:
    op.drop_table("ai_analysis")
    op.drop_table("ai_message")
    op.drop_table("ai_session")
    op.drop_table("knowledge_chunk")
    op.drop_table("knowledge_document")
    op.drop_table("work_item")
    op.drop_index("ix_train_project_course_id", table_name="train_project")
    op.drop_column("train_project", "course_id")
