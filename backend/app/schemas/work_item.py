from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WorkItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assignee_id: int
    creator_id: int | None
    task_type: str
    biz_type: str
    biz_id: int
    title: str
    description: str | None
    priority: int
    status: int
    due_time: datetime | None
    resolved_time: datetime | None
    create_time: datetime

