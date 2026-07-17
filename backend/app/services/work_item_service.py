"""Event-driven work item helpers."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.work_item import WorkItem


def ensure_work_item(
    db: Session,
    *,
    assignee_id: int,
    task_type: str,
    biz_type: str,
    biz_id: int,
    title: str,
    creator_id: int | None = None,
    description: str | None = None,
    priority: int = 2,
    due_time=None,
) -> WorkItem:
    item = db.scalar(select(WorkItem).where(
        WorkItem.assignee_id == assignee_id,
        WorkItem.task_type == task_type,
        WorkItem.biz_type == biz_type,
        WorkItem.biz_id == biz_id,
        WorkItem.status == 0,
        WorkItem.is_deleted == 0,
    ))
    if item:
        return item
    item = WorkItem(
        assignee_id=assignee_id, creator_id=creator_id, task_type=task_type,
        biz_type=biz_type, biz_id=biz_id, title=title, description=description,
        priority=priority, due_time=due_time, status=0,
    )
    db.add(item)
    db.flush()
    return item


def complete_work_items(
    db: Session, *, assignee_id: int | None = None, task_type: str | None = None,
    biz_type: str, biz_id: int,
) -> int:
    stmt = select(WorkItem).where(
        WorkItem.biz_type == biz_type,
        WorkItem.biz_id == biz_id,
        WorkItem.status == 0,
        WorkItem.is_deleted == 0,
    )
    if assignee_id is not None:
        stmt = stmt.where(WorkItem.assignee_id == assignee_id)
    if task_type is not None:
        stmt = stmt.where(WorkItem.task_type == task_type)
    items = list(db.scalars(stmt).all())
    now = datetime.now(timezone.utc)
    for item in items:
        item.status = 1
        item.resolved_time = now
        db.add(item)
    return len(items)
