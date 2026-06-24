"""评价指标模型。"""
from decimal import Decimal

from sqlalchemy import BigInteger, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class EvalIndicator(Base, TimestampMixin):
    """评价指标表（支持按项目配置的多级指标体系）。"""

    __tablename__ = "eval_indicator"

    project_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True, comment="所属项目ID；NULL表示通用模板指标"
    )
    parent_id: Mapped[int] = mapped_column(
        BigInteger, default=0, index=True, comment="父级指标ID，0为一级指标"
    )
    indicator_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="指标名称"
    )
    indicator_code: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False, comment="指标编码（项目内唯一）"
    )
    weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=0, comment="权重（百分比，同级合计应为100）"
    )
    max_score: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), default=100, comment="满分值"
    )
    scoring_rule: Mapped[str | None] = mapped_column(
        String(1000), comment="评分标准/细则"
    )
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态：1-启用 0-停用")
