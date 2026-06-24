"""实训成果模型。"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TrainAchievement(Base, TimestampMixin):
    """实训成果表（学生针对项目提交的成果）。"""

    __tablename__ = "train_achievement"

    project_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="所属项目ID"
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="提交学生ID"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="成果标题")
    content: Mapped[str | None] = mapped_column(LONGTEXT, comment="成果文本内容")
    attachment_url: Mapped[str | None] = mapped_column(String(500), comment="附件URL")
    repo_url: Mapped[str | None] = mapped_column(String(255), comment="代码仓库地址")
    version: Mapped[int] = mapped_column(Integer, default=1, comment="提交版本号")
    submit_time: Mapped[datetime | None] = mapped_column(DateTime, comment="提交时间")
    status: Mapped[int] = mapped_column(
        Integer, default=0, index=True,
        comment="状态：0-草稿 1-已提交 2-评价中 3-已评价 4-退回重做",
    )
    final_score: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), comment="最终综合得分"
    )
