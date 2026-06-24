"""用户路由：演示 CRUD 与角色权限控制。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.auth import CurrentUser
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services.user_service import user_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post(
    "",
    summary="创建用户（仅管理员）",
    dependencies=[Depends(require_roles(RoleCode.ADMIN))],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = user_service.create_user(db, payload)
    return success(data=UserOut.model_validate(user).model_dump(), msg="创建成功")


@router.get(
    "",
    summary="用户列表（教师/管理员）",
)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role_id: int | None = Query(None, description="按角色ID过滤"),
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    offset = (page - 1) * page_size
    filters = {"role_id": role_id} if role_id is not None else {}
    items = user_service.list(db, offset=offset, limit=page_size, **filters)
    total = user_service.count(db, **filters)
    return success(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [UserOut.model_validate(u).model_dump() for u in items],
        }
    )


@router.get("/{user_id}", summary="用户详情（登录可访问）")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    user = user_service.get(db, user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    return success(data=UserOut.model_validate(user).model_dump())


@router.put(
    "/{user_id}",
    summary="更新用户（仅管理员）",
    dependencies=[Depends(require_roles(RoleCode.ADMIN))],
)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = user_service.update_user(db, user_id, payload)
    return success(data=UserOut.model_validate(user).model_dump(), msg="更新成功")


@router.delete(
    "/{user_id}",
    summary="删除用户（逻辑删除，仅管理员）",
    dependencies=[Depends(require_roles(RoleCode.ADMIN))],
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if not user_service.remove(db, user_id):
        raise BusinessException("用户不存在", code=404)
    return success(msg="删除成功")
