"""实训项目 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    project_name: str = Field(..., max_length=150, description="项目名称")
    project_code: str = Field(..., max_length=64, description="项目编码")
    org_id: int | None = Field(default=None, description="归属组织ID")
    teacher_id: int = Field(..., description="负责教师ID")
    category: str | None = Field(default=None, max_length=50, description="项目类别")
    difficulty: int = Field(default=2, description="难度：1-初级 2-中级 3-高级")
    description: str | None = Field(default=None, description="项目描述与要求")
    start_time: datetime | None = Field(default=None, description="开始时间")
    end_time: datetime | None = Field(default=None, description="结束时间")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_name: str | None = Field(default=None, max_length=150)
    org_id: int | None = None
    teacher_id: int | None = None
    category: str | None = None
    difficulty: int | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: int | None = Field(default=None, description="0-未开始 1-进行中 2-已结束 3-已归档")


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: int
    create_time: datetime
