"""Pydantic schemas for training projects."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    project_name: str = Field(..., max_length=150, description="Project name")
    project_code: str = Field(..., max_length=64, description="Unique project code")
    org_id: int | None = Field(default=None, description="Organization ID")
    course_id: int | None = Field(default=None, description="Owning course ID")
    teacher_id: int = Field(..., description="Teacher user ID")
    enterprise_id: int | None = Field(default=None, description="Enterprise mentor user ID")
    category: str | None = Field(default=None, max_length=50, description="Category")
    difficulty: int = Field(default=2, description="1-basic 2-medium 3-advanced")
    description: str | None = Field(default=None, description="Project requirements")
    start_time: datetime | None = Field(default=None, description="Start time")
    end_time: datetime | None = Field(default=None, description="End time")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(default=None, max_length=150)
    org_id: int | None = None
    course_id: int | None = None
    teacher_id: int | None = None
    enterprise_id: int | None = None
    category: str | None = None
    difficulty: int | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: int | None = Field(default=None, description="0-not started 1-active 2-ended 3-archived")


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: int
    create_time: datetime
