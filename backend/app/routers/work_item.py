from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import BusinessException
from app.core.response import success
from app.models.work_item import WorkItem
from app.schemas.auth import CurrentUser
from app.schemas.work_item import WorkItemOut

router = APIRouter(prefix="/work-items", tags=["任务中心"])


@router.get("")
def list_work_items(
    status: int | None = Query(None, ge=0, le=2),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    filters = [WorkItem.assignee_id == current.user_id, WorkItem.is_deleted == 0]
    if status is not None:
        filters.append(WorkItem.status == status)
    stmt = select(WorkItem).where(*filters).order_by(
        WorkItem.status.asc(), WorkItem.priority.desc(), WorkItem.due_time.asc(), WorkItem.id.desc()
    )
    count_stmt = select(func.count()).select_from(WorkItem).where(*filters)
    items = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    return success(data={
        "total": db.scalar(count_stmt) or 0,
        "page": page,
        "page_size": page_size,
        "items": [WorkItemOut.model_validate(item).model_dump() for item in items],
    })


@router.post("/{item_id}/complete")
def complete_work_item(
    item_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    item = db.get(WorkItem, item_id)
    if not item or item.is_deleted == 1:
        raise BusinessException("任务不存在", code=404)
    if item.assignee_id != current.user_id:
        raise BusinessException("无权操作该任务", code=403)
    if item.task_type != "VIEW_FEEDBACK":
        raise BusinessException("请在对应业务页面完成该任务", code=400)
    item.status = 1
    item.resolved_time = datetime.now(timezone.utc)
    db.add(item)
    db.commit()
    db.refresh(item)
    return success(data=WorkItemOut.model_validate(item).model_dump(), msg="任务已完成")
