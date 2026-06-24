"""SQLAlchemy 2.0 声明基类与公共字段 Mixin。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 ORM 模型的声明基类。"""


class TimestampMixin:
    """公共字段：主键、创建/更新时间、逻辑删除。"""

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    is_deleted: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0", comment="逻辑删除：0-未删除 1-已删除"
    )
