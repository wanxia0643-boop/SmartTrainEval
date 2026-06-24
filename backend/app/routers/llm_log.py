"""大模型调用日志路由（只读，管理员）。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.llm_log import LlmLogOut
from app.services.llm_log_service import llm_log_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/llm-logs", tags=["大模型调用日志"])


@router.get("", summary="调用日志列表（管理员）",
            dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def list_llm_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = llm_log_service.list(db, offset=(page - 1) * page_size, limit=page_size)
    return success(data={
        "total": llm_log_service.count(db),
        "page": page,
        "page_size": page_size,
        "items": [LlmLogOut.model_validate(x).model_dump() for x in items],
    })


@router.get("/{log_id}", summary="调用日志详情（管理员）",
            dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def get_llm_log(log_id: int, db: Session = Depends(get_db)):
    obj = llm_log_service.get(db, log_id)
    if not obj:
        raise BusinessException("日志不存在", code=404)
    return success(data=LlmLogOut.model_validate(obj).model_dump())
