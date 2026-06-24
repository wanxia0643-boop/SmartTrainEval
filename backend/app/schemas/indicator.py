"""评价指标 schema。"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class IndicatorBase(BaseModel):
    project_id: int | None = Field(default=None, description="所属项目ID；NULL为通用模板")
    parent_id: int = Field(default=0, description="父级指标ID，0为一级")
    indicator_name: str = Field(..., max_length=100, description="指标名称")
    indicator_code: str = Field(..., max_length=64, description="指标编码")
    weight: Decimal = Field(default=Decimal("0"), description="权重（百分比）")
    max_score: Decimal = Field(default=Decimal("100"), description="满分值")
    scoring_rule: str | None = Field(default=None, max_length=1000, description="评分标准")
    sort: int = Field(default=0, description="排序")


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorUpdate(BaseModel):
    indicator_name: str | None = Field(default=None, max_length=100)
    parent_id: int | None = None
    weight: Decimal | None = None
    max_score: Decimal | None = None
    scoring_rule: str | None = None
    sort: int | None = None
    status: int | None = None


class IndicatorOut(IndicatorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: int
    create_time: datetime
