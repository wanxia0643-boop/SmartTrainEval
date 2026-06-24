"""FastAPI 依赖：当前用户解析与角色权限校验。"""
from collections.abc import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.exceptions import AuthException, PermissionException
from app.core.security import decode_access_token
from app.schemas.auth import CurrentUser
from app.utils.enums import RoleCode

# tokenUrl 指向登录接口，供 Swagger “Authorize” 使用
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_prefix}/auth/login/form", auto_error=False
)


def get_current_user(token: str | None = Depends(oauth2_scheme)) -> CurrentUser:
    """解析 JWT，返回当前登录用户上下文。"""
    if not token:
        raise AuthException("缺少认证令牌")
    payload = decode_access_token(token)
    if not payload:
        raise AuthException("令牌无效或已过期")
    user_id = payload.get("sub")
    if user_id is None:
        raise AuthException("令牌缺少用户信息")
    return CurrentUser(
        user_id=int(user_id),
        username=payload.get("username", ""),
        role_code=payload.get("role_code", ""),
    )


def require_roles(*roles: RoleCode) -> Callable[..., CurrentUser]:
    """生成「需要指定角色之一」的依赖。

    用法：
        @router.get("/x", dependencies=[Depends(require_roles(RoleCode.ADMIN))])
        # 或注入当前用户：
        def handler(user: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN))):
    """
    allowed = {r.value for r in roles}

    def _checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role_code not in allowed:
            raise PermissionException(
                f"当前角色[{user.role_code or '未知'}]无权访问，需要：{', '.join(allowed)}"
            )
        return user

    return _checker
