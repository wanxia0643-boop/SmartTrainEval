"""Course enrollment service."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment


class CourseEnrollmentService:
    """Course enrollment service."""

    def enroll(self, db: Session, course_id: int, student_id: int) -> CourseEnrollment:
        """Enroll student in course."""
        enrollment = CourseEnrollment(
            course_id=course_id,
            student_id=student_id,
            status=1,
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    def get_by_student_and_course(self, db: Session, student_id: int, course_id: int) -> CourseEnrollment | None:
        """Check if student is enrolled in course."""
        stmt = select(CourseEnrollment).where(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.is_deleted == 0,
        )
        return db.scalars(stmt).first()

    def list_by_student(self, db: Session, student_id: int, offset: int = 0, limit: int = 10) -> list[CourseEnrollment]:
        """List all enrollments for a student."""
        stmt = select(CourseEnrollment).where(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.is_deleted == 0,
            CourseEnrollment.status == 1,
        )
        stmt = stmt.offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    def count_by_student(self, db: Session, student_id: int) -> int:
        """Count enrollments for a student."""
        from sqlalchemy import func
        stmt = select(func.count()).select_from(CourseEnrollment).where(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.is_deleted == 0,
            CourseEnrollment.status == 1,
        )
        return db.scalar(stmt) or 0

    def drop(self, db: Session, enrollment_id: int) -> bool:
        """Drop course (soft delete)."""
        enrollment = db.get(CourseEnrollment, enrollment_id)
        if not enrollment or enrollment.is_deleted == 1:
            return False
        enrollment.is_deleted = 1
        db.add(enrollment)
        db.commit()
        return True


course_enrollment_service = CourseEnrollmentService()
