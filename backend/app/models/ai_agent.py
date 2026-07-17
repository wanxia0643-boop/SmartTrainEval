"""Persisted AI sessions, messages, and structured analyses."""
from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AISession(Base, TimestampMixin):
    __tablename__ = "ai_session"

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    course_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    project_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    scene: Mapped[str] = mapped_column(String(40), default="COACH", index=True)
    title: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[int] = mapped_column(Integer, default=1, index=True)


class AIMessage(Base, TimestampMixin):
    __tablename__ = "ai_message"

    session_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    citations_json: Mapped[str | None] = mapped_column(LONGTEXT)


class AIAnalysis(Base, TimestampMixin):
    __tablename__ = "ai_analysis"

    user_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    scene: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    biz_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    biz_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    status: Mapped[int] = mapped_column(Integer, default=1, index=True)
    result_json: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    citations_json: Mapped[str | None] = mapped_column(LONGTEXT)
    model_name: Mapped[str | None] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(40), default="v1")
    llm_log_id: Mapped[int | None] = mapped_column(BigInteger, index=True)

