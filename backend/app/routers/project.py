"""Training project routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.access import (
    ensure_project_read,
    ensure_project_write,
    is_admin,
    is_enterprise,
    is_student,
    is_teacher,
)
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.models.project import TrainProject
from app.schemas.auth import CurrentUser
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.project_service import project_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/projects", tags=["实训项目"])


def _project_filters(stmt, user: CurrentUser):
    stmt = stmt.where(TrainProject.is_deleted == 0)
    if is_admin(user):
        return stmt
    if is_teacher(user):
        return stmt.where(TrainProject.teacher_id == user.user_id)
    if is_enterprise(user):
        return stmt.where(TrainProject.enterprise_id == user.user_id)
    if is_student(user):
        return stmt.where(TrainProject.status != 3)
    return stmt.where(False)


@router.post("", summary="创建项目（教师/管理员）")
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    if project_service.get_by(db, project_code=payload.project_code):
        raise BusinessException("项目编码已存在", code=409)
    data = payload.model_dump()
    if is_teacher(current):
        data["teacher_id"] = current.user_id
    obj = project_service.create(db, data)
    return success(data=ProjectOut.model_validate(obj).model_dump(), msg="创建成功")


@router.get("", summary="项目列表")
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    stmt = _project_filters(select(TrainProject), current).order_by(TrainProject.id.desc())
    count_stmt = _project_filters(
        select(func.count()).select_from(TrainProject), current
    )
    items = db.scalars(stmt.offset(offset).limit(page_size)).all()
    return success(data={
        "total": db.scalar(count_stmt) or 0,
        "page": page,
        "page_size": page_size,
        "items": [ProjectOut.model_validate(p).model_dump() for p in items],
    })


@router.get("/{project_id}", summary="项目详情")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    obj = ensure_project_read(db, project_id, current)
    return success(data=ProjectOut.model_validate(obj).model_dump())


@router.put("/{project_id}", summary="更新项目（教师/管理员）")
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    obj = ensure_project_write(db, project_id, current)
    data = payload.model_dump(exclude_unset=True)
    if is_teacher(current):
        data.pop("teacher_id", None)
    obj = project_service.update(db, obj, data)
    return success(data=ProjectOut.model_validate(obj).model_dump(), msg="更新成功")


@router.delete("/{project_id}", summary="删除项目（管理员）")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_roles(RoleCode.ADMIN)),
):
    if not project_service.remove(db, project_id):
        raise BusinessException("项目不存在", code=404)
    return success(msg="删除成功")
