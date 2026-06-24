"""组织机构模型。"""
from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Org(Base, TimestampMixin):
    """组织机构表（学校/学院/专业/班级/企业，树形）。"""

    __tablename__ = "sys_org"

    org_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="组织名称")
    org_code: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="组织编码"
    )
    org_type: Mapped[int] = mapped_column(
        Integer, default=1, comment="类型：1-学校 2-学院 3-专业 4-班级 5-企业"
    )
    parent_id: Mapped[int] = mapped_column(
        BigInteger, default=0, index=True, comment="父级ID，0为顶级"
    )
    ancestors: Mapped[str] = mapped_column(
        String(500), default="", comment="祖级路径，逗号分隔"
    )
    leader: Mapped[str | None] = mapped_column(String(50), comment="负责人")
    contact: Mapped[str | None] = mapped_column(String(30), comment="联系电话")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态：1-启用 0-停用")
