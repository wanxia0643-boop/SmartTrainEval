"""用户相关 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """用户公共字段。"""

    username: str = Field(..., min_length=2, max_length=50, description="登录账号")
    real_name: str = Field(..., max_length=50, description="真实姓名")
    role_id: int = Field(..., description="角色ID")
    org_id: int | None = Field(default=None, description="组织ID")
    student_no: str | None = Field(default=None, max_length=50, description="学号/工号")
    gender: int = Field(default=0, description="性别：0-未知 1-男 2-女")
    email: EmailStr | None = Field(default=None, description="邮箱")
    phone: str | None = Field(default=None, max_length=30, description="手机号")


class UserCreate(UserBase):
    """创建用户。"""

    password: str = Field(..., min_length=6, max_length=64, description="登录密码")


class UserUpdate(BaseModel):
    """更新用户（所有字段可选）。"""

    real_name: str | None = Field(default=None, max_length=50)
    role_id: int | None = None
    org_id: int | None = None
    email: EmailStr | None = None
    phone: str | None = None
    status: int | None = None


class UserOut(BaseModel):
    """用户输出（脱敏，不含密码）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str
    nickname: str | None
    role_id: int
    org_id: int | None
    student_no: str | None
    gender: int
    email: str | None
    phone: str | None
    avatar: str | None
    status: int
    create_time: datetime
