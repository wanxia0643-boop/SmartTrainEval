"""Role-aware work item model."""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class WorkItem(Base, TimestampMixin):
    __tablename__ = "work_item"

    assignee_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    creator_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    task_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    biz_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    biz_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, default=2, index=True)
    status: Mapped[int] = mapped_column(Integer, default=0, index=True)
    due_time: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    resolved_time: Mapped[datetime | None] = mapped_column(DateTime)

