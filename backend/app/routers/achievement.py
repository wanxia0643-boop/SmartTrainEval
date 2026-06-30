"""Training achievement routes."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.access import (
    ensure_achievement_read,
    ensure_project_read,
    get_project_or_404,
    is_admin,
    is_enterprise,
    is_student,
    is_teacher,
)
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException, PermissionException
from app.core.response import success
from app.models.achievement import TrainAchievement
from app.models.project import TrainProject
from app.schemas.achievement import AchievementCreate, AchievementOut, AchievementUpdate
from app.schemas.auth import CurrentUser
from app.services.achievement_service import achievement_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/achievements", tags=["实训成果"])


def _achievement_scope(stmt, user: CurrentUser):
    stmt = stmt.where(TrainAchievement.is_deleted == 0)
    if is_admin(user):
        return stmt
    if is_student(user):
        return stmt.where(TrainAchievement.student_id == user.user_id)
    stmt = stmt.join(TrainProject, TrainAchievement.project_id == TrainProject.id).where(
        TrainProject.is_deleted == 0
    )
    if is_teacher(user):
        return stmt.where(TrainProject.teacher_id == user.user_id)
    if is_enterprise(user):
        return stmt.where(TrainProject.enterprise_id == user.user_id)
    return stmt.where(False)


def _apply_filters(stmt, project_id: int | None, student_id: int | None):
    if project_id is not None:
        stmt = stmt.where(TrainAchievement.project_id == project_id)
    if student_id is not None:
        stmt = stmt.where(TrainAchievement.student_id == student_id)
    return stmt


@router.post("", summary="提交成果（学生）")
def create_achievement(
    payload: AchievementCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.STUDENT)),
):
    project = ensure_project_read(db, payload.project_id, current)
    if project.status == 3:
        raise BusinessException("项目已归档，不能提交成果", code=400)
    data = payload.model_dump()
    data["student_id"] = current.user_id
    data["status"] = 1
    data["submit_time"] = datetime.now(timezone.utc)
    obj = achievement_service.create(db, data)
    return success(data=AchievementOut.model_validate(obj).model_dump(), msg="提交成功")


@router.get("", summary="成果列表（按角色自动过滤）")
def list_achievements(
    project_id: int | None = Query(None),
    student_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    offset = (page - 1) * page_size
    effective_student_id = current.user_id if is_student(current) else student_id
    stmt = _apply_filters(
        _achievement_scope(select(TrainAchievement), current),
        project_id,
        effective_student_id,
    ).order_by(TrainAchievement.id.desc())
    count_stmt = _apply_filters(
        _achievement_scope(select(func.count()).select_from(TrainAchievement), current),
        project_id,
        effective_student_id,
    )
    items = db.scalars(stmt.offset(offset).limit(page_size)).all()
    return success(data={
        "total": db.scalar(count_stmt) or 0,
        "page": page,
        "page_size": page_size,
        "items": [AchievementOut.model_validate(a).model_dump() for a in items],
    })


@router.get("/{achievement_id}", summary="成果详情")
def get_achievement(
    achievement_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    obj, _ = ensure_achievement_read(db, achievement_id, current)
    return success(data=AchievementOut.model_validate(obj).model_dump())


@router.put("/{achievement_id}", summary="更新成果（学生/教师/管理员）")
def update_achievement(
    achievement_id: int,
    payload: AchievementUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.STUDENT, RoleCode.TEACHER, RoleCode.ADMIN)),
):
    obj, project = ensure_achievement_read(db, achievement_id, current)
    data = payload.model_dump(exclude_unset=True)

    if is_student(current):
        if obj.student_id != current.user_id:
            raise PermissionException("只能修改自己的成果")
        if obj.status in (2, 3):
            raise BusinessException("成果已进入评价流程，不能由学生修改", code=400)
        data = {
            k: v for k, v in data.items()
            if k in {"title", "content", "attachment_url", "repo_url"}
        }
        data["status"] = 1
        data["submit_time"] = datetime.now(timezone.utc)
    elif is_teacher(current):
        if project.teacher_id != current.user_id:
            raise PermissionException("无权维护该成果")
        data = {k: v for k, v in data.items() if k in {"status", "final_score"}}
    elif not is_admin(current):
        raise PermissionException("无权维护该成果")

    obj = achievement_service.update(db, obj, data)
    return success(data=AchievementOut.model_validate(obj).model_dump(), msg="更新成功")


@router.delete("/{achievement_id}", summary="删除成果（教师/管理员）")
def delete_achievement(
    achievement_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    obj = achievement_service.get(db, achievement_id)
    if not obj:
        raise BusinessException("成果不存在", code=404)
    project = get_project_or_404(db, obj.project_id)
    if is_teacher(current) and project.teacher_id != current.user_id:
        raise PermissionException("无权删除该成果")
    if not achievement_service.remove(db, achievement_id):
        raise BusinessException("成果不存在", code=404)
    return success(msg="删除成功")
