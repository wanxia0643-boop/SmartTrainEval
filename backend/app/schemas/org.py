"""组织 schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrgBase(BaseModel):
    org_name: str = Field(..., max_length=100, description="组织名称")
    org_code: str = Field(..., max_length=64, description="组织编码")
    org_type: int = Field(default=1, description="类型：1-学校 2-学院 3-专业 4-班级 5-企业")
    parent_id: int = Field(default=0, description="父级ID，0为顶级")
    leader: str | None = Field(default=None, max_length=50, description="负责人")
    contact: str | None = Field(default=None, max_length=30, description="联系电话")
    sort: int = Field(default=0, description="排序")


class OrgCreate(OrgBase):
    pass


class OrgUpdate(BaseModel):
    org_name: str | None = Field(default=None, max_length=100)
    org_type: int | None = None
    parent_id: int | None = None
    leader: str | None = None
    contact: str | None = None
    sort: int | None = None
    status: int | None = None


class OrgOut(OrgBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ancestors: str
    status: int
    create_time: datetime
