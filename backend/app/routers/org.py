"""组织机构路由。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.org import OrgCreate, OrgOut, OrgUpdate
from app.services.org_service import org_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/orgs", tags=["组织机构"])


@router.post("", summary="创建组织（管理员）",
             dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def create_org(payload: OrgCreate, db: Session = Depends(get_db)):
    if org_service.get_by(db, org_code=payload.org_code):
        raise BusinessException("组织编码已存在", code=409)
    obj = org_service.create(db, payload.model_dump())
    return success(data=OrgOut.model_validate(obj).model_dump(), msg="创建成功")


@router.get("", summary="组织列表", dependencies=[Depends(get_current_user)])
def list_orgs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = org_service.list(db, offset=(page - 1) * page_size, limit=page_size)
    return success(data={
        "total": org_service.count(db),
        "page": page,
        "page_size": page_size,
        "items": [OrgOut.model_validate(o).model_dump() for o in items],
    })


@router.get("/{org_id}", summary="组织详情", dependencies=[Depends(get_current_user)])
def get_org(org_id: int, db: Session = Depends(get_db)):
    obj = org_service.get(db, org_id)
    if not obj:
        raise BusinessException("组织不存在", code=404)
    return success(data=OrgOut.model_validate(obj).model_dump())


@router.put("/{org_id}", summary="更新组织（管理员）",
            dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def update_org(org_id: int, payload: OrgUpdate, db: Session = Depends(get_db)):
    obj = org_service.get(db, org_id)
    if not obj:
        raise BusinessException("组织不存在", code=404)
    obj = org_service.update(db, obj, payload.model_dump(exclude_unset=True))
    return success(data=OrgOut.model_validate(obj).model_dump(), msg="更新成功")


@router.delete("/{org_id}", summary="删除组织（管理员）",
               dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def delete_org(org_id: int, db: Session = Depends(get_db)):
    if not org_service.remove(db, org_id):
        raise BusinessException("组织不存在", code=404)
    return success(msg="删除成功")
