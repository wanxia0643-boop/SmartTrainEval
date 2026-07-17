"""Course folder ORM model."""
from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CourseFolder(Base, TimestampMixin):
    """A folder for organizing courses."""

    __tablename__ = "course_folder"

    folder_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Folder name"
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="Teacher user ID"
    )
    org_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True, comment="Organization ID"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, comment="Sort order"
    )
