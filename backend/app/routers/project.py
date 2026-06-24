"""实训项目路由。"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.project_service import project_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/projects", tags=["实训项目"])


@router.post("", summary="创建项目（教师/管理员）",
             dependencies=[Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN))])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    if project_service.get_by(db, project_code=payload.project_code):
        raise BusinessException("项目编码已存在", code=409)
    obj = project_service.create(db, payload.model_dump())
    return success(data=ProjectOut.model_validate(obj).model_dump(), msg="创建成功")


@router.get("", summary="项目列表", dependencies=[Depends(get_current_user)])
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items = project_service.list(db, offset=(page - 1) * page_size, limit=page_size)
    return success(data={
        "total": project_service.count(db),
        "page": page,
        "page_size": page_size,
        "items": [ProjectOut.model_validate(p).model_dump() for p in items],
    })


@router.get("/{project_id}", summary="项目详情", dependencies=[Depends(get_current_user)])
def get_project(project_id: int, db: Session = Depends(get_db)):
    obj = project_service.get(db, project_id)
    if not obj:
        raise BusinessException("项目不存在", code=404)
    return success(data=ProjectOut.model_validate(obj).model_dump())


@router.put("/{project_id}", summary="更新项目（教师/管理员）",
            dependencies=[Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN))])
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    obj = project_service.get(db, project_id)
    if not obj:
        raise BusinessException("项目不存在", code=404)
    obj = project_service.update(db, obj, payload.model_dump(exclude_unset=True))
    return success(data=ProjectOut.model_validate(obj).model_dump(), msg="更新成功")


@router.delete("/{project_id}", summary="删除项目（管理员）",
               dependencies=[Depends(require_roles(RoleCode.ADMIN))])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    if not project_service.remove(db, project_id):
        raise BusinessException("项目不存在", code=404)
    return success(msg="删除成功")
