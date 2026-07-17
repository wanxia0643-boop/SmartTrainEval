"""Course ORM model."""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Course(Base, TimestampMixin):
    """A course managed by teachers."""

    __tablename__ = "course"

    course_name: Mapped[str] = mapped_column(
        String(150), nullable=False, comment="Course name"
    )
    course_code: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="Unique course code"
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="Teacher user ID"
    )
    org_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True, comment="Organization ID"
    )
    category: Mapped[str | None] = mapped_column(
        String(50), comment="Course category"
    )
    description: Mapped[str | None] = mapped_column(
        Text, comment="Course description"
    )
    start_date: Mapped[datetime | None] = mapped_column(
        DateTime, comment="Course start date"
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime, comment="Course end date"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        default=1,
        index=True,
        comment="Status: 0-disabled 1-active 2-ended",
    )
    max_students: Mapped[int | None] = mapped_column(
        Integer, comment="Maximum number of students"
    )
    credits: Mapped[int | None] = mapped_column(
        Integer, comment="Course credits"
    )
    cover_image: Mapped[str | None] = mapped_column(
        String(300), comment="Course cover image URL"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, comment="Sort order (smaller = higher priority, pinned=-1)"
    )
