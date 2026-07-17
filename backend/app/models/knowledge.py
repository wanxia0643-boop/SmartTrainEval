"""Course and project knowledge base models."""
from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_document"

    course_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    project_id: Mapped[int | None] = mapped_column(BigInteger, index=True)
    uploader_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[int] = mapped_column(Integer, default=1, index=True)
    error_msg: Mapped[str | None] = mapped_column(String(1000))


class KnowledgeChunk(Base, TimestampMixin):
    __tablename__ = "knowledge_chunk"

    document_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    source_label: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    keywords: Mapped[str | None] = mapped_column(Text)

