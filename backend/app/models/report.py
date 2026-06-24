"""报表记录模型。"""
from typing import Any

from sqlalchemy import JSON, BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ReportRecord(Base, TimestampMixin):
    """报表记录表。"""

    __tablename__ = "report_record"

    report_name: Mapped[str] = mapped_column(
        String(150), nullable=False, comment="报表名称"
    )
    report_type: Mapped[int] = mapped_column(
        Integer, default=1, index=True,
        comment="类型：1-学生成绩 2-项目评价 3-组织汇总 4-AI使用统计",
    )
    project_id: Mapped[int | None] = mapped_column(BigInteger, index=True, comment="关联项目ID")
    org_id: Mapped[int | None] = mapped_column(BigInteger, comment="关联组织ID")
    generator_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False, comment="生成人ID"
    )
    file_format: Mapped[str] = mapped_column(
        String(20), default="PDF", comment="文件格式：PDF/EXCEL/WORD"
    )
    file_url: Mapped[str | None] = mapped_column(String(500), comment="报表文件URL")
    params: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, comment="生成参数（查询条件快照）"
    )
    status: Mapped[int] = mapped_column(
        Integer, default=0, comment="状态：0-生成中 1-成功 2-失败"
    )
    remark: Mapped[str | None] = mapped_column(String(500), comment="备注")
