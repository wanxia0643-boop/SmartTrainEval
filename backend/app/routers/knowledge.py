from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.access import (
    ensure_course_read, ensure_project_read, is_admin, is_enterprise, is_student, is_teacher,
)
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import BusinessException
from app.core.response import success
from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.models.project import TrainProject
from app.schemas.auth import CurrentUser
from app.schemas.knowledge import KnowledgeDocumentOut
from app.services.knowledge_service import chunk_text
from app.utils.file_extract import extract_text

router = APIRouter(prefix="/knowledge", tags=["课程知识库"])
BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads" / "knowledge"
ALLOWED = {".pdf", ".docx", ".txt", ".md", ".json", ".csv", ".zip", ".py", ".java", ".js", ".ts", ".vue"}


def _can_manage(db: Session, current: CurrentUser, course_id: int, project_id: int | None):
    if is_admin(current):
        return
    if is_teacher(current):
        course = db.get(Course, course_id)
        if course and course.is_deleted == 0 and course.teacher_id == current.user_id:
            return
    if is_enterprise(current) and project_id:
        project = ensure_project_read(db, project_id, current)
        if project.course_id == course_id:
            return
    raise BusinessException("无权维护该知识库", code=403)


@router.post("/documents")
async def upload_document(
    course_id: int = Form(...),
    project_id: int | None = Form(None),
    title: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    _can_manage(db, current, course_id, project_id)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED:
        raise BusinessException("不支持的知识资料类型", code=400)
    raw = await file.read()
    if not raw or len(raw) > 30 * 1024 * 1024:
        raise BusinessException("文件不能为空且不能超过 30MB", code=400)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}{suffix}"
    path = UPLOAD_DIR / name
    path.write_bytes(raw)
    document = KnowledgeDocument(
        course_id=course_id,
        project_id=project_id,
        uploader_id=current.user_id,
        title=(title or Path(file.filename or name).stem)[:200],
        file_name=(file.filename or name)[:255],
        file_url=f"/uploads/knowledge/{name}",
        mime_type=file.content_type,
        status=0,
    )
    db.add(document)
    db.flush()
    try:
        text = extract_text(path)
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("未提取到可检索文本")
        for index, content in enumerate(chunks):
            db.add(KnowledgeChunk(
                document_id=document.id,
                chunk_index=index,
                source_label=f"第 {index + 1} 段",
                content=content,
            ))
        document.status = 1
    except Exception as exc:
        document.status = 2
        document.error_msg = str(exc)[:1000]
    db.add(document)
    db.commit()
    db.refresh(document)
    return success(data=KnowledgeDocumentOut.model_validate(document).model_dump(), msg="资料已入库")


@router.get("/documents")
def list_documents(
    course_id: int | None = Query(None),
    project_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    if course_id:
        if is_enterprise(current):
            if not project_id:
                raise BusinessException("企业导师查询知识库时需指定项目", code=400)
            ensure_project_read(db, project_id, current)
        else:
            ensure_course_read(db, course_id, current)
    stmt = select(KnowledgeDocument).where(KnowledgeDocument.is_deleted == 0)
    if course_id:
        stmt = stmt.where(KnowledgeDocument.course_id == course_id)
    if project_id:
        stmt = stmt.where(or_(KnowledgeDocument.project_id.is_(None), KnowledgeDocument.project_id == project_id))
    if is_teacher(current):
        own_courses = select(Course.id).where(Course.teacher_id == current.user_id, Course.is_deleted == 0)
        stmt = stmt.where(KnowledgeDocument.course_id.in_(own_courses))
    elif is_enterprise(current):
        own_projects = select(TrainProject.id).where(TrainProject.enterprise_id == current.user_id, TrainProject.is_deleted == 0)
        stmt = stmt.where(KnowledgeDocument.project_id.in_(own_projects))
    elif is_student(current):
        enrolled = select(CourseEnrollment.course_id).where(
            CourseEnrollment.student_id == current.user_id,
            CourseEnrollment.status == 1,
            CourseEnrollment.is_deleted == 0,
        )
        stmt = stmt.where(KnowledgeDocument.course_id.in_(enrolled))
    items = db.scalars(stmt.order_by(KnowledgeDocument.id.desc())).all()
    return success(data=[KnowledgeDocumentOut.model_validate(item).model_dump() for item in items])


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    document = db.get(KnowledgeDocument, document_id)
    if not document or document.is_deleted == 1:
        raise BusinessException("资料不存在", code=404)
    _can_manage(db, current, document.course_id, document.project_id)
    document.is_deleted = 1
    db.add(document)
    db.commit()
    return success(msg="资料已删除")

