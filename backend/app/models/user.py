"""用户模型。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """用户表。"""

    __tablename__ = "sys_user"

    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="登录账号"
    )
    password: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="BCrypt 加密密码"
    )
    real_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="真实姓名")
    nickname: Mapped[str | None] = mapped_column(String(50), comment="昵称")
    role_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="角色ID"
    )
    org_id: Mapped[int | None] = mapped_column(BigInteger, index=True, comment="组织ID")
    student_no: Mapped[str | None] = mapped_column(String(50), comment="学号/工号")
    gender: Mapped[int] = mapped_column(Integer, default=0, comment="性别：0-未知 1-男 2-女")
    email: Mapped[str | None] = mapped_column(String(100), comment="邮箱")
    phone: Mapped[str | None] = mapped_column(String(30), comment="手机号")
    avatar: Mapped[str | None] = mapped_column(String(255), comment="头像URL")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态：1-正常 0-禁用")
    last_login_time: Mapped[datetime | None] = mapped_column(
        DateTime, comment="最后登录时间"
    )
