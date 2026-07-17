"""Course enrollment ORM model — links students to courses."""
from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CourseEnrollment(Base, TimestampMixin):
    """Student enrollment record for a course."""

    __tablename__ = "course_enrollment"

    course_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="Course ID"
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="Student user ID"
    )
    status: Mapped[int] = mapped_column(
        Integer, default=1, comment="Enrollment status: 1-enrolled 2-dropped"
    )
