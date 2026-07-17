"""Report record and download routes."""
from pathlib import Path

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.access import is_admin
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException, PermissionException
from app.core.response import success
from app.schemas.auth import CurrentUser
from app.schemas.report import ReportCreate, ReportOut, ReportUpdate
from app.services.report_exporter import BACKEND_DIR, generate_report_file
from app.services.report_service import report_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/reports", tags=["报表记录"])


def _ensure_report_access(report, current: CurrentUser):
    if is_admin(current) or report.generator_id == current.user_id:
        return
    raise PermissionException("无权访问该报表")


def _report_path(file_url: str | None) -> Path:
    if not file_url:
        raise BusinessException("报表文件不存在", code=404)
    path = (BACKEND_DIR / file_url.lstrip("/")).resolve()
    try:
        path.relative_to((BACKEND_DIR / "generated").resolve())
    except ValueError as exc:
        raise BusinessException("报表文件路径非法", code=400) from exc
    if not path.exists():
        raise BusinessException("报表文件不存在", code=404)
    return path


@router.post("", summary="生成报表（教师/管理员）")
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    data = payload.model_dump()
    data["generator_id"] = current.user_id
    data["status"] = 0
    data["params"] = data.get("params") or {
        "project_id": payload.project_id,
        "org_id": payload.org_id,
        "report_type": payload.report_type,
    }
    obj = report_service.create(db, data)
    try:
        file_url = generate_report_file(
            db,
            report_type=payload.report_type,
            project_id=payload.project_id,
            file_format=payload.file_format,
            current=current,
        )
        obj = report_service.update(db, obj, {
            "file_url": file_url,
            "status": 1,
            "remark": f"已生成 {payload.file_format} 文件",
        })
    except Exception as exc:
        obj = report_service.update(db, obj, {
            "status": 2,
            "remark": str(exc)[:500],
        })
    return success(data=ReportOut.model_validate(obj).model_dump(), msg="生成完成")


@router.get("", summary="报表列表")
def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    filters = {} if is_admin(current) else {"generator_id": current.user_id}
    items = report_service.list(db, offset=(page - 1) * page_size, limit=page_size, **filters)
    return success(data={
        "total": report_service.count(db, **filters),
        "page": page,
        "page_size": page_size,
        "items": [ReportOut.model_validate(r).model_dump() for r in items],
    })


@router.get("/{report_id}", summary="报表详情")
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    obj = report_service.get(db, report_id)
    if not obj:
        raise BusinessException("报表不存在", code=404)
    _ensure_report_access(obj, current)
    return success(data=ReportOut.model_validate(obj).model_dump())


@router.get("/{report_id}/download", summary="下载报表")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    obj = report_service.get(db, report_id)
    if not obj:
        raise BusinessException("报表不存在", code=404)
    _ensure_report_access(obj, current)
    path = _report_path(obj.file_url)
    media_types = {
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pdf": "application/pdf",
        ".csv": "text/csv; charset=utf-8",
    }
    return FileResponse(
        path=str(path),
        filename=path.name,
        media_type=media_types.get(path.suffix.lower(), "application/octet-stream"),
    )


@router.put("/{report_id}", summary="更新报表（教师/管理员）")
def update_report(
    report_id: int,
    payload: ReportUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    obj = report_service.get(db, report_id)
    if not obj:
        raise BusinessException("报表不存在", code=404)
    _ensure_report_access(obj, current)
    obj = report_service.update(db, obj, payload.model_dump(exclude_unset=True))
    return success(data=ReportOut.model_validate(obj).model_dump(), msg="更新成功")


@router.delete("/{report_id}", summary="删除报表（管理员）")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_roles(RoleCode.ADMIN)),
):
    if not report_service.remove(db, report_id):
        raise BusinessException("报表不存在", code=404)
    return success(msg="删除成功")
