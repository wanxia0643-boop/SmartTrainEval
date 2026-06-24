"""评价结果模型。"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EvalResult(Base, TimestampMixin):
    """评价结果表（某成果在某指标上的一次评分，支持 AI 与人工）。"""

    __tablename__ = "eval_result"

    achievement_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="实训成果ID"
    )
    indicator_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="评价指标ID"
    )
    eval_type: Mapped[int] = mapped_column(
        Integer, default=1, index=True,
        comment="评价方式：1-AI 2-教师 3-企业导师 4-学生自评",
    )
    evaluator_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True, comment="评价人ID（人工评价时）"
    )
    llm_log_id: Mapped[int | None] = mapped_column(
        BigInteger, comment="大模型调用日志ID（AI评价时）"
    )
    score: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=0, comment="该指标得分")
    comment: Mapped[str | None] = mapped_column(Text, comment="评语/评价意见")
    suggestion: Mapped[str | None] = mapped_column(Text, comment="改进建议")
    eval_time: Mapped[datetime | None] = mapped_column(DateTime, comment="评价时间")
