"""Course folder API router."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.auth import CurrentUser
from app.schemas.course_folder import (
    CourseFolderCreate,
    CourseFolderOut,
    CourseFolderUpdate,
)
from app.services.course_folder_service import course_folder_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/course-folders", tags=["课程文件夹"])


@router.post("", summary="创建文件夹（教师/管理员）")
def create_folder(
    payload: CourseFolderCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    """创建新课程文件夹。"""
    data = payload.model_dump()
    data["teacher_id"] = current.user_id
    if current.role_code == RoleCode.TEACHER.value:
        data["org_id"] = current.org_id
    folder = course_folder_service.create(db, CourseFolderCreate(**data))
    return success(data=CourseFolderOut.model_validate(folder).model_dump(), msg="创建成功")


@router.get("", summary="文件夹列表")
def list_folders(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """获取当前教师的文件夹列表。"""
    folders, total = course_folder_service.list(db, current.user_id, page, page_size)
    return success(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [CourseFolderOut.model_validate(f).model_dump() for f in folders],
        }
    )


@router.put("/{folder_id}", summary="更新文件夹")
def update_folder(
    folder_id: int,
    payload: CourseFolderUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """更新文件夹信息。"""
    folder = course_folder_service.get(db, folder_id)
    if not folder or folder.is_deleted == 1:
        raise BusinessException("文件夹不存在", code=404)
    if current.role_code == RoleCode.TEACHER.value and folder.teacher_id != current.user_id:
        raise BusinessException("无权修改该文件夹", code=403)
    folder = course_folder_service.update(db, folder, payload)
    return success(data=CourseFolderOut.model_validate(folder).model_dump(), msg="更新成功")


@router.delete("/{folder_id}", summary="删除文件夹")
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """删除文件夹（软删除）。"""
    folder = course_folder_service.get(db, folder_id)
    if not folder or folder.is_deleted == 1:
        raise BusinessException("文件夹不存在", code=404)
    if current.role_code == RoleCode.TEACHER.value and folder.teacher_id != current.user_id:
        raise BusinessException("无权删除该文件夹", code=403)
    course_folder_service.remove(db, folder_id)
    return success(msg="删除成功")
