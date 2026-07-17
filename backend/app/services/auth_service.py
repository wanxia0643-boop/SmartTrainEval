"""认证业务逻辑：登录、签发令牌。"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthException
from app.core.security import create_access_token, verify_password
from app.models.role import Role
from app.schemas.auth import LoginRequest, TokenData
from app.services.user_service import user_service


class AuthService:
    """登录认证服务。"""

    def login(self, db: Session, payload: LoginRequest) -> TokenData:
        user = user_service.get_by_username(db, payload.username)
        if not user or not verify_password(payload.password, user.password):
            raise AuthException("用户名或密码错误", code=401)
        if user.status != 1:
            raise AuthException("账号已被禁用", code=403)

        role = db.get(Role, user.role_id)
        role_code = role.role_code if role else ""

        token = create_access_token(
            subject=user.id,
            extra_claims={
                "username": user.username,
                "role_code": role_code,
                "real_name": user.real_name,
                "org_id": user.org_id,
            },
        )

        # 记录最后登录时间
        user.last_login_time = datetime.now(timezone.utc)
        db.add(user)
        db.commit()

        return TokenData(
            access_token=token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )


auth_service = AuthService()
