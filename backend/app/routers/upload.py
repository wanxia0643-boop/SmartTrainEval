"""File upload routes."""
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.deps import get_current_user
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.auth import CurrentUser
from app.utils.file_extract import extract_text

router = APIRouter(prefix="/uploads", tags=["文件上传"])

BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_ROOT = BACKEND_DIR / "uploads"
MAX_UPLOAD_BYTES = 30 * 1024 * 1024
ALLOWED_SUFFIXES = {
    ".txt", ".md", ".pdf", ".docx", ".zip", ".rar", ".7z",
    ".py", ".java", ".js", ".ts", ".vue", ".html", ".css", ".sql",
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
}


@router.post("", summary="上传成果附件")
async def upload_file(
    file: UploadFile = File(...),
    _: CurrentUser = Depends(get_current_user),
):
    original_name = file.filename or "attachment"
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise BusinessException("不支持的文件类型", code=400)

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise BusinessException("文件不能超过 30MB", code=400)

    date_dir = datetime.now().strftime("%Y%m%d")
    target_dir = UPLOAD_ROOT / date_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    saved_name = f"{uuid4().hex}{suffix}"
    saved_path = target_dir / saved_name
    saved_path.write_bytes(content)

    text = extract_text(saved_path)
    file_url = f"/uploads/{date_dir}/{saved_name}"
    return success(data={
        "file_name": original_name,
        "file_url": file_url,
        "size": len(content),
        "content_type": file.content_type,
        "extracted_text": text,
    }, msg="上传成功")
