"""Pydantic schemas for course enrollment."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseEnrollmentCreate(BaseModel):
    """Enroll in a course by course code."""
    course_code: str = Field(..., max_length=64, description="Course code")


class CourseEnrollmentOut(BaseModel):
    """Enrollment output schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    student_id: int
    status: int
    create_time: datetime
