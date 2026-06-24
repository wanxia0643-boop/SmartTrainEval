"""安全相关：密码哈希与 JWT 令牌。"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# bcrypt 单次最多处理 72 字节，超出部分按惯例截断
_BCRYPT_MAX_BYTES = 72


def hash_password(plain_password: str) -> str:
    """对明文密码做 BCrypt 哈希。"""
    pwd = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pwd, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希是否匹配。"""
    pwd = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    try:
        return bcrypt.checkpw(pwd, hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(
    subject: str | int,
    extra_claims: dict[str, Any] | None = None,
    expires_minutes: int | None = None,
) -> str:
    """生成 JWT 访问令牌。

    Args:
        subject: 令牌主体，通常为用户 ID。
        extra_claims: 附加声明，如 role_code、username。
        expires_minutes: 过期时间（分钟），默认取配置。
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.jwt_access_token_expire_minutes
    )
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """解码并校验 JWT；无效返回 None。"""
    try:
        return jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        return None
