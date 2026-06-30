"""Common enums."""
from enum import Enum


class RoleCode(str, Enum):
    """System role codes."""

    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ENTERPRISE = "ENTERPRISE"
    ADMIN = "ADMIN"
