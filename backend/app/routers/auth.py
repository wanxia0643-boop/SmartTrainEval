"""认证路由：登录、获取当前用户信息、更新个人资料。"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import BusinessException
from app.core.response import success
from app.models.user import User
from app.schemas.auth import CurrentUser, LoginRequest, ProfileUpdate, UserProfile
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", summary="账号密码登录（JSON）")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login(db, payload)
    return success(data=token.model_dump(), msg="登录成功")


@router.post("/login/form", summary="OAuth2 表单登录（供 Swagger 授权使用）")
def login_form(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    token = auth_service.login(
        db, LoginRequest(username=form.username, password=form.password)
    )
    # OAuth2 规范要求顶层返回 access_token/token_type，供 Swagger 解析
    return token.model_dump()


@router.get("/me", summary="获取当前登录用户信息")
def me(current: CurrentUser = Depends(get_current_user)):
    return success(data=current.model_dump())


@router.get("/profile", summary="获取当前用户完整资料")
def get_profile(
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.get(User, current.user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    profile = UserProfile(
        user_id=user.id,
        username=user.username,
        role_code=current.role_code,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        org_id=user.org_id,
        student_no=user.student_no,
        gender=user.gender,
        avatar=user.avatar,
    )
    return success(data=profile.model_dump())


@router.put("/profile", summary="更新当前用户个人资料")
def update_profile(
    payload: ProfileUpdate,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.get(User, current.user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return success(msg="个人资料已更新")
