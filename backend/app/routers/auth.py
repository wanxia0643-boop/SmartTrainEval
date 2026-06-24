"""认证路由：登录。"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.schemas.auth import CurrentUser, LoginRequest
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
