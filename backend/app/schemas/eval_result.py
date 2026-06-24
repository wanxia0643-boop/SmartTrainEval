"""评价结果 schema。"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class EvalResultBase(BaseModel):
    achievement_id: int = Field(..., description="实训成果ID")
    indicator_id: int = Field(..., description="评价指标ID")
    eval_type: int = Field(default=1, description="评价方式：1-AI 2-教师 3-企业导师 4-自评")
    evaluator_id: int | None = Field(default=None, description="评价人ID（人工评价时）")
    llm_log_id: int | None = Field(default=None, description="大模型调用日志ID（AI评价时）")
    score: Decimal = Field(default=Decimal("0"), description="该指标得分")
    comment: str | None = Field(default=None, description="评语")
    suggestion: str | None = Field(default=None, description="改进建议")


class EvalResultCreate(EvalResultBase):
    pass


class EvalResultUpdate(BaseModel):
    score: Decimal | None = None
    comment: str | None = None
    suggestion: str | None = None


class EvalResultOut(EvalResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    eval_time: datetime | None
    create_time: datetime
