"""Evaluation result routes."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.access import (
    ensure_achievement_read,
    ensure_achievement_review,
    get_achievement_or_404,
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
from app.models.eval_result import EvalResult
from app.models.indicator import EvalIndicator
from app.models.project import TrainProject
from app.schemas.auth import CurrentUser
from app.schemas.eval_result import EvalResultCreate, EvalResultOut, EvalResultUpdate
from app.services.eval_result_service import eval_result_service
from app.services.work_item_service import complete_work_items, ensure_work_item
from app.utils.enums import RoleCode

router = APIRouter(prefix="/eval-results", tags=["评价结果"])

_EVALUATOR_ROLES = (RoleCode.TEACHER, RoleCode.ENTERPRISE)


def _role_eval_type(user: CurrentUser, requested: int | None) -> int:
    if is_teacher(user):
        return 2
    if is_enterprise(user):
        return 3
    raise PermissionException("当前角色不能参与常规评分")


def _eval_scope(stmt, user: CurrentUser):
    stmt = stmt.where(EvalResult.is_deleted == 0)
    if is_admin(user):
        return stmt
    stmt = stmt.join(TrainAchievement, EvalResult.achievement_id == TrainAchievement.id).where(
        TrainAchievement.is_deleted == 0
    )
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


def _apply_result_filters(stmt, achievement_id: int | None):
    if achievement_id is not None:
        stmt = stmt.where(EvalResult.achievement_id == achievement_id)
    return stmt


@router.post("", summary="录入评价（教师/企业导师/管理员）")
def create_eval_result(
    payload: EvalResultCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(*_EVALUATOR_ROLES)),
):
    achievement, project = ensure_achievement_review(db, payload.achievement_id, current)
    indicator = db.get(EvalIndicator, payload.indicator_id)
    if not indicator or indicator.is_deleted == 1:
        raise BusinessException("评价指标不存在", code=404)
    if indicator.project_id not in (None, achievement.project_id):
        raise BusinessException("评价指标不属于该成果项目", code=400)

    data = payload.model_dump()
    data["evaluator_id"] = current.user_id
    data["eval_type"] = _role_eval_type(current, data.get("eval_type"))
    data["eval_time"] = datetime.now(timezone.utc)
    existing = db.scalar(select(EvalResult).where(
        EvalResult.achievement_id == payload.achievement_id,
        EvalResult.indicator_id == payload.indicator_id,
        EvalResult.eval_type == data["eval_type"],
        EvalResult.evaluator_id == current.user_id,
        EvalResult.is_deleted == 0,
    ))
    if existing:
        obj = eval_result_service.update(db, existing, data)
    else:
        obj = eval_result_service.create(db, data)
    final = eval_result_service.recalc_final_score(db, obj.achievement_id)
    if eval_result_service.is_role_complete(db, obj.achievement_id, obj.eval_type):
        task_type = "TEACHER_REVIEW" if obj.eval_type == 2 else "ENTERPRISE_REVIEW"
        complete_work_items(
            db, assignee_id=current.user_id, task_type=task_type,
            biz_type="ACHIEVEMENT", biz_id=obj.achievement_id,
        )
    if final is not None:
        ensure_work_item(
            db, assignee_id=achievement.student_id, creator_id=current.user_id,
            task_type="VIEW_FEEDBACK", biz_type="ACHIEVEMENT", biz_id=achievement.id,
            title=f"查看评价反馈：{achievement.title}", priority=2,
        )
    db.commit()
    return success(
        data={**EvalResultOut.model_validate(obj).model_dump(), "final_score": final},
        msg="评价成功",
    )


@router.get("", summary="评价结果列表（按角色自动过滤）")
def list_eval_results(
    achievement_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    if achievement_id is not None:
        ensure_achievement_read(db, achievement_id, current)
    offset = (page - 1) * page_size
    stmt = _apply_result_filters(
        _eval_scope(select(EvalResult), current), achievement_id
    ).order_by(EvalResult.id.desc())
    count_stmt = _apply_result_filters(
        _eval_scope(select(func.count()).select_from(EvalResult), current),
        achievement_id,
    )
    items = db.scalars(stmt.offset(offset).limit(page_size)).all()
    return success(data={
        "total": db.scalar(count_stmt) or 0,
        "page": page,
        "page_size": page_size,
        "items": [EvalResultOut.model_validate(r).model_dump() for r in items],
    })


@router.put("/{result_id}", summary="修订评价（教师/企业导师/管理员）")
def update_eval_result(
    result_id: int,
    payload: EvalResultUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(*_EVALUATOR_ROLES)),
):
    obj = eval_result_service.get(db, result_id)
    if not obj:
        raise BusinessException("评价结果不存在", code=404)
    achievement, project = ensure_achievement_review(db, obj.achievement_id, current)
    role_matches = (
        is_admin(current)
        or obj.evaluator_id == current.user_id
        or (is_teacher(current) and project.teacher_id == current.user_id and obj.eval_type == 2)
        or (is_enterprise(current) and project.enterprise_id == current.user_id and obj.eval_type == 3)
    )
    if not role_matches:
        raise PermissionException("无权修订该评价")

    obj = eval_result_service.update(db, obj, payload.model_dump(exclude_unset=True))
    final = eval_result_service.recalc_final_score(db, achievement.id)
    if eval_result_service.is_role_complete(db, achievement.id, obj.eval_type):
        task_type = "TEACHER_REVIEW" if obj.eval_type == 2 else "ENTERPRISE_REVIEW"
        complete_work_items(
            db, assignee_id=current.user_id, task_type=task_type,
            biz_type="ACHIEVEMENT", biz_id=achievement.id,
        )
    if final is not None:
        ensure_work_item(
            db, assignee_id=achievement.student_id, creator_id=current.user_id,
            task_type="VIEW_FEEDBACK", biz_type="ACHIEVEMENT", biz_id=achievement.id,
            title=f"查看评价反馈：{achievement.title}", priority=2,
        )
    db.commit()
    return success(
        data={**EvalResultOut.model_validate(obj).model_dump(), "final_score": final},
        msg="更新成功",
    )


@router.delete("/{result_id}", summary="删除评价（管理员）")
def delete_eval_result(
    result_id: int,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_roles(RoleCode.ADMIN)),
):
    obj = eval_result_service.get(db, result_id)
    if not obj:
        raise BusinessException("评价结果不存在", code=404)
    achievement_id = obj.achievement_id
    eval_result_service.remove(db, result_id)
    eval_result_service.recalc_final_score(db, achievement_id)
    return success(msg="删除成功")


@router.post("/recalc/{achievement_id}", summary="重新汇总成果得分（教师/企业导师/管理员）")
def recalc_final_score(
    achievement_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(*_EVALUATOR_ROLES)),
):
    ensure_achievement_review(db, achievement_id, current)
    final = eval_result_service.recalc_final_score(db, achievement_id)
    achievement = get_achievement_or_404(db, achievement_id)
    return success(
        data={
            "achievement_id": achievement_id,
            "status": achievement.status,
            "final_score": final,
        },
        msg="汇总完成",
    )
