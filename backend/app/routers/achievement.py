"""实训成果路由。"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.achievement import AchievementCreate, AchievementOut, AchievementUpdate
from app.schemas.auth import CurrentUser
from app.services.achievement_service import achievement_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/achievements", tags=["实训成果"])


@router.post("", summary="提交成果（学生）",
             dependencies=[Depends(require_roles(RoleCode.STUDENT))])
def create_achievement(
    payload: AchievementCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.STUDENT)),
):
    data = payload.model_dump()
    # 强制以当前登录学生为提交人，提交即标记已提交
    data["student_id"] = current.user_id
    data["status"] = 1
    data["submit_time"] = datetime.now(timezone.utc)
    obj = achievement_service.create(db, data)
    return success(data=AchievementOut.model_validate(obj).model_dump(), msg="提交成功")


@router.get("", summary="成果列表（可按项目/学生过滤）",
            dependencies=[Depends(get_current_user)])
def list_achievements(
    project_id: int | None = Query(None),
    student_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = {k: v for k, v in {"project_id": project_id, "student_id": student_id}.items()
               if v is not None}
    items = achievement_service.list(
        db, offset=(page - 1) * page_size, limit=page_size, **filters
    )
    return success(data={
        "total": achievement_service.count(db, **filters),
        "page": page,
        "page_size": page_size,
        "items": [AchievementOut.model_validate(a).model_dump() for a in items],
    })


@router.get("/{achievement_id}", summary="成果详情",
            dependencies=[Depends(get_current_user)])
def get_achievement(achievement_id: int, db: Session = Depends(get_db)):
    obj = achievement_service.get(db, achievement_id)
    if not obj:
        raise BusinessException("成果不存在", code=404)
    return success(data=AchievementOut.model_validate(obj).model_dump())


@router.put("/{achievement_id}", summary="更新成果（学生/教师）",
            dependencies=[Depends(require_roles(RoleCode.STUDENT, RoleCode.TEACHER))])
def update_achievement(
    achievement_id: int, payload: AchievementUpdate, db: Session = Depends(get_db)
):
    obj = achievement_service.get(db, achievement_id)
    if not obj:
        raise BusinessException("成果不存在", code=404)
    obj = achievement_service.update(db, obj, payload.model_dump(exclude_unset=True))
    return success(data=AchievementOut.model_validate(obj).model_dump(), msg="更新成功")


@router.delete("/{achievement_id}", summary="删除成果（教师/管理员）",
               dependencies=[Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN))])
def delete_achievement(achievement_id: int, db: Session = Depends(get_db)):
    if not achievement_service.remove(db, achievement_id):
        raise BusinessException("成果不存在", code=404)
    return success(msg="删除成功")
