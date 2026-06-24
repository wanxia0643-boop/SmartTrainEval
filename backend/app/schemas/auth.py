"""认证相关 schema。"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求。"""

    username: str = Field(..., min_length=2, max_length=50, description="登录账号")
    password: str = Field(..., min_length=6, max_length=64, description="登录密码")


class TokenData(BaseModel):
    """登录成功返回的令牌数据。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="过期时间（秒）")


class CurrentUser(BaseModel):
    """从 JWT 解析出的当前用户上下文。"""

    user_id: int
    username: str
    role_code: str
    real_name: str = ""
