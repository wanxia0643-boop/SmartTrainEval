"""角色模型。"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Role(Base, TimestampMixin):
    """用户角色表。"""

    __tablename__ = "sys_role"

    role_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="角色名称")
    role_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="角色编码，如 STUDENT/TEACHER"
    )
    data_scope: Mapped[int] = mapped_column(
        Integer, default=1, comment="数据范围：1-本人 2-本组织 3-全部"
    )
    description: Mapped[str | None] = mapped_column(String(255), comment="角色描述")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态：1-启用 0-停用")
