"""大模型调用日志 schema（一般由系统写入，对外多为只读）。"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LlmLogCreate(BaseModel):
    # model_name 字段与 Pydantic 保留前缀 model_ 冲突，显式放开
    model_config = ConfigDict(protected_namespaces=())

    user_id: int | None = None
    biz_type: str | None = Field(default=None, max_length=50)
    biz_id: int | None = None
    model_name: str = Field(..., max_length=80, description="模型名称")
    request_id: str | None = Field(default=None, max_length=80)
    prompt_text: str | None = None
    response_text: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: Decimal = Decimal("0")
    duration_ms: int = 0
    status: int = Field(default=1, description="1-成功 0-失败")
    error_msg: str | None = Field(default=None, max_length=1000)


class LlmLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    user_id: int | None
    biz_type: str | None
    biz_id: int | None
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: Decimal
    duration_ms: int
    status: int
    create_time: datetime
