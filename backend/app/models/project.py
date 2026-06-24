"""实训项目模型。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class TrainProject(Base, TimestampMixin):
    """实训项目表。"""

    __tablename__ = "train_project"

    project_name: Mapped[str] = mapped_column(
        String(150), nullable=False, comment="项目名称"
    )
    project_code: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="项目编码"
    )
    org_id: Mapped[int | None] = mapped_column(BigInteger, index=True, comment="归属组织ID")
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="负责教师ID"
    )
    category: Mapped[str | None] = mapped_column(String(50), comment="项目类别")
    difficulty: Mapped[int] = mapped_column(
        Integer, default=2, comment="难度：1-初级 2-中级 3-高级"
    )
    description: Mapped[str | None] = mapped_column(Text, comment="项目描述与要求")
    start_time: Mapped[datetime | None] = mapped_column(DateTime, comment="开始时间")
    end_time: Mapped[datetime | None] = mapped_column(DateTime, comment="结束时间")
    status: Mapped[int] = mapped_column(
        Integer, default=0, index=True, comment="状态：0-未开始 1-进行中 2-已结束 3-已归档"
    )
