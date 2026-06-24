"""报表记录 schema。"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReportBase(BaseModel):
    report_name: str = Field(..., max_length=150, description="报表名称")
    report_type: int = Field(
        default=1, description="类型：1-学生成绩 2-项目评价 3-组织汇总 4-AI使用统计"
    )
    project_id: int | None = Field(default=None, description="关联项目ID")
    org_id: int | None = Field(default=None, description="关联组织ID")
    file_format: str = Field(default="PDF", max_length=20, description="格式：PDF/EXCEL/WORD")
    params: dict[str, Any] | None = Field(default=None, description="生成参数快照")


class ReportCreate(ReportBase):
    generator_id: int = Field(..., description="生成人ID")


class ReportUpdate(BaseModel):
    file_url: str | None = Field(default=None, max_length=500)
    status: int | None = Field(default=None, description="0-生成中 1-成功 2-失败")
    remark: str | None = Field(default=None, max_length=500)


class ReportOut(ReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    generator_id: int
    file_url: str | None
    status: int
    remark: str | None
    create_time: datetime
