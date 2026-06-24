"""角色路由（只读，登录可访问）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.schemas.role import RoleOut
from app.services.role_service import role_service

router = APIRouter(prefix="/roles", tags=["角色"])


@router.get("", summary="角色列表", dependencies=[Depends(get_current_user)])
def list_roles(db: Session = Depends(get_db)):
    items = role_service.list(db, offset=0, limit=100)
    return success(data=[RoleOut.model_validate(r).model_dump() for r in items])
