"""通用枚举：角色编码等。"""
from enum import StrEnum


class RoleCode(StrEnum):
    """系统四种角色编码。"""

    STUDENT = "STUDENT"        # 学生
    TEACHER = "TEACHER"        # 教师
    ENTERPRISE = "ENTERPRISE"  # 企业导师
    ADMIN = "ADMIN"            # 管理员
