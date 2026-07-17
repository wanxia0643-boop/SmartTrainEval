"""Training project ORM model."""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TrainProject(Base, TimestampMixin):
    """A practical training project managed by a teacher."""

    __tablename__ = "train_project"

    project_name: Mapped[str] = mapped_column(
        String(150), nullable=False, comment="Project name"
    )
    project_code: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="Unique project code"
    )
    org_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True, comment="Organization ID"
    )
    course_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True, comment="Owning course ID"
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="Teacher user ID"
    )
    enterprise_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True, comment="Enterprise mentor user ID"
    )
    category: Mapped[str | None] = mapped_column(String(50), comment="Category")
    difficulty: Mapped[int] = mapped_column(
        Integer, default=2, comment="Difficulty: 1-basic 2-medium 3-advanced"
    )
    description: Mapped[str | None] = mapped_column(
        Text, comment="Project description and requirements"
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime, comment="Start time")
    end_time: Mapped[datetime | None] = mapped_column(DateTime, comment="End time")
    status: Mapped[int] = mapped_column(
        Integer,
        default=0,
        index=True,
        comment="Status: 0-not started 1-active 2-ended 3-archived",
    )
