from datetime import datetime

from pydantic import BaseModel, ConfigDict


class KnowledgeDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int | None
    project_id: int | None
    uploader_id: int
    title: str
    file_name: str
    file_url: str
    mime_type: str | None
    status: int
    error_msg: str | None
    create_time: datetime


class Citation(BaseModel):
    document_id: int
    title: str
    chunk_id: int
    source_label: str | None = None
    excerpt: str

