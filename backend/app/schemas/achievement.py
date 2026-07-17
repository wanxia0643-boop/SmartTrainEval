"""实训成果 schema。"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AchievementBase(BaseModel):
    project_id: int = Field(..., description="所属项目ID")
    student_id: int = Field(..., description="提交学生ID")
    title: str = Field(..., max_length=200, description="成果标题")
    content: str | None = Field(default=None, description="成果文本内容")
    attachment_url: str | None = Field(default=None, max_length=500, description="附件URL")
    repo_url: str | None = Field(default=None, max_length=255, description="代码仓库地址")


class AchievementCreate(AchievementBase):
    status: int = Field(default=1, ge=0, le=1, description="0-保存草稿 1-正式提交")


class AchievementUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = None
    attachment_url: str | None = None
    repo_url: str | None = None
    status: int | None = Field(default=None, description="0-草稿 1-已提交 2-评价中 3-已评价 4-退回")
    final_score: Decimal | None = None


class AchievementOut(AchievementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: int
    submit_time: datetime | None
    status: int
    final_score: Decimal | None
    create_time: datetime
