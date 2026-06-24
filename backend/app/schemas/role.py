"""角色 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RoleOut(BaseModel):
    """角色输出。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role_name: str
    role_code: str
    data_scope: int
    description: str | None
    sort: int
    status: int
    create_time: datetime
