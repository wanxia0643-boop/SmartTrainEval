"""Pydantic schemas for course folders."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseFolderBase(BaseModel):
    """Course folder base fields."""

    folder_name: str = Field(..., max_length=100, description="Folder name")
    teacher_id: int | None = Field(default=None, description="Teacher user ID (auto-set)")
    org_id: int | None = Field(default=None, description="Organization ID")
    sort_order: int = Field(default=0, description="Sort order")


class CourseFolderCreate(CourseFolderBase):
    """Create course folder."""
    pass


class CourseFolderUpdate(BaseModel):
    """Update course folder."""

    folder_name: str | None = Field(default=None, max_length=100)
    sort_order: int | None = None


class CourseFolderOut(CourseFolderBase):
    """Course folder output schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    create_time: datetime
