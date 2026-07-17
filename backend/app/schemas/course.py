"""Pydantic schemas for courses."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    """Course base fields."""

    course_name: str = Field(..., max_length=150, description="Course name")
    course_code: str = Field(..., max_length=64, description="Unique course code")
    teacher_id: int | None = Field(default=None, description="Teacher user ID (auto-set from current user)")
    org_id: int | None = Field(default=None, description="Organization ID")
    category: str | None = Field(default=None, max_length=50, description="Course category")
    description: str | None = Field(default=None, description="Course description")
    start_date: datetime | None = Field(default=None, description="Course start date")
    end_date: datetime | None = Field(default=None, description="Course end date")
    max_students: int | None = Field(default=None, description="Maximum number of students")
    credits: int | None = Field(default=None, description="Course credits")
    cover_image: str | None = Field(default=None, max_length=300, description="Course cover image URL")


class CourseCreate(CourseBase):
    """Create course."""

    pass


class CourseUpdate(BaseModel):
    """Update course (all fields optional)."""

    course_name: str | None = Field(default=None, max_length=150)
    org_id: int | None = None
    teacher_id: int | None = None
    category: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: int | None = Field(default=None, description="0-disabled 1-active 2-ended")
    max_students: int | None = None
    credits: int | None = None
    cover_image: str | None = None
    sort_order: int | None = None


class CourseOut(CourseBase):
    """Course output schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: int
    sort_order: int = 0
    create_time: datetime
