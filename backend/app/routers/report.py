"""报表记录路由。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.report import ReportCreate, ReportOut, ReportUpdate
from app.services.report_service import report_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/reports", tags=["报表记录"])


@router.post("", summary="生成报表记录（教师/管理员）",
             dependencies=[Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN))])
def create_report(payload: ReportCreate, db: Session = Depends(get_db)):
    obj = report_service.create(db, payload.model_dump())
    return success(data=ReportOut.model_validate(obj).model_dump(), msg="创建成功")


@router.get("", summary="报表列表", dependencies=[Depends(get_current_user)])
def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = report_service.list(db, offset=(page - 1) * page_size, limit=page_size)
    return success(data={
        "total": report_service.count(db),
        "page": page,
        "page_size": page_size,
        "items": [ReportOut.model_validate(r).model_dump() for r in items],
    })


@router.get("/{report_id}", summary="报表详情", dependencies=[Depends(get_current_user)])
def get_report(report_id: int, db: Session = Depends(get_db)):
    obj = report_service.get(db, report_id)
    if not obj:
        raise BusinessException("报表不存在", code=404)
    return success(data=ReportOut.model_validate(obj).model_dump())


@router.put("/{report_id}", summary="更新报表（教师/管理员）",
            dependencies=[Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN))])
def update_report(report_id: int, payload: ReportUpdate, db: Session = Depends(get_db)):
    obj = report_service.get(db, report_id)
    if not obj:
        raise BusinessException("报表不存在", code=404)
    obj = report_service.update(db, obj, payload.model_dump(exclude_unset=True))
    return success(data=ReportOut.model_validate(obj).model_dump(), msg="更新成功")


@router.delete("/{report_id}", summary="删除报表（管理员）",
               dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def delete_report(report_id: int, db: Session = Depends(get_db)):
    if not report_service.remove(db, report_id):
        raise BusinessException("报表不存在", code=404)
    return success(msg="删除成功")
