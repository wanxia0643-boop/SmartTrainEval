"""Evaluation indicator routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.access import ensure_project_read, ensure_project_write, is_admin
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException, PermissionException
from app.core.response import success
from app.schemas.auth import CurrentUser
from app.schemas.indicator import IndicatorCreate, IndicatorOut, IndicatorUpdate
from app.services.indicator_service import indicator_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/indicators", tags=["评价指标"])


def _ensure_indicator_write(db: Session, indicator_id: int, current: CurrentUser):
    obj = indicator_service.get(db, indicator_id)
    if not obj:
        raise BusinessException("指标不存在", code=404)
    if obj.project_id is None:
        if not is_admin(current):
            raise PermissionException("只有管理员可以维护通用指标")
        return obj
    ensure_project_write(db, obj.project_id, current)
    return obj


@router.post("", summary="创建指标（教师/管理员）")
def create_indicator(
    payload: IndicatorCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    if payload.project_id is None and not is_admin(current):
        raise PermissionException("教师只能为自己的项目创建指标")
    if payload.project_id is not None:
        ensure_project_write(db, payload.project_id, current)
    obj = indicator_service.create(db, payload.model_dump())
    return success(data=IndicatorOut.model_validate(obj).model_dump(), msg="创建成功")


@router.get("", summary="指标列表（可按项目过滤）")
def list_indicators(
    project_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    if project_id is not None:
        ensure_project_read(db, project_id, current)
    filters = {"project_id": project_id} if project_id is not None else {}
    items = indicator_service.list(
        db, offset=(page - 1) * page_size, limit=page_size, **filters
    )
    return success(data={
        "total": indicator_service.count(db, **filters),
        "page": page,
        "page_size": page_size,
        "items": [IndicatorOut.model_validate(i).model_dump() for i in items],
    })


@router.put("/{indicator_id}", summary="更新指标（教师/管理员）")
def update_indicator(
    indicator_id: int,
    payload: IndicatorUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    obj = _ensure_indicator_write(db, indicator_id, current)
    obj = indicator_service.update(db, obj, payload.model_dump(exclude_unset=True))
    return success(data=IndicatorOut.model_validate(obj).model_dump(), msg="更新成功")


@router.delete("/{indicator_id}", summary="删除指标（教师/管理员）")
def delete_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    _ensure_indicator_write(db, indicator_id, current)
    if not indicator_service.remove(db, indicator_id):
        raise BusinessException("指标不存在", code=404)
    return success(msg="删除成功")
