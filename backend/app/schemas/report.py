"""Pydantic schemas for report records."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReportBase(BaseModel):
    report_name: str = Field(..., max_length=150, description="Report name")
    report_type: int = Field(default=1, description="1-score 2-project 3-org 4-ai usage")
    project_id: int | None = Field(default=None, description="Project ID")
    org_id: int | None = Field(default=None, description="Organization ID")
    file_format: str = Field(default="EXCEL", max_length=20, description="EXCEL/PDF/WORD")
    params: dict[str, Any] | None = Field(default=None, description="Query params snapshot")


class ReportCreate(ReportBase):
    generator_id: int | None = Field(default=None, description="Generator user ID")


class ReportUpdate(BaseModel):
    file_url: str | None = Field(default=None, max_length=500)
    status: int | None = Field(default=None, description="0-generating 1-success 2-failed")
    remark: str | None = Field(default=None, max_length=500)


class ReportOut(ReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    generator_id: int
    file_url: str | None
    status: int
    remark: str | None
    create_time: datetime
