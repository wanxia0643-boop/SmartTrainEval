"""大模型调用日志模型。"""
from decimal import Decimal

from sqlalchemy import BigInteger, Integer, Numeric, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LlmCallLog(Base, TimestampMixin):
    """大模型调用日志表。"""

    __tablename__ = "llm_call_log"

    user_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True, comment="触发调用的用户ID"
    )
    biz_type: Mapped[str | None] = mapped_column(
        String(50), index=True, comment="业务类型，如 ACHIEVEMENT_EVAL/REPORT_GEN"
    )
    biz_id: Mapped[int | None] = mapped_column(BigInteger, comment="关联业务主键ID")
    model_name: Mapped[str] = mapped_column(
        String(80), index=True, nullable=False, comment="模型名称"
    )
    request_id: Mapped[str | None] = mapped_column(String(80), comment="上游请求ID")
    prompt_text: Mapped[str | None] = mapped_column(LONGTEXT, comment="请求提示词")
    response_text: Mapped[str | None] = mapped_column(LONGTEXT, comment="模型返回内容")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="输入token数")
    completion_tokens: Mapped[int] = mapped_column(
        Integer, default=0, comment="输出token数"
    )
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="总token数")
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0, comment="费用（元）")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, comment="耗时（毫秒）")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态：1-成功 0-失败")
    error_msg: Mapped[str | None] = mapped_column(String(1000), comment="失败原因")
