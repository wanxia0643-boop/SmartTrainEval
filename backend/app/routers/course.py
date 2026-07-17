"""Course routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.auth import CurrentUser
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate
from app.services.course_service import course_service
from app.utils.enums import RoleCode

router = APIRouter(prefix="/courses", tags=["课程管理"])


@router.post("", summary="创建课程（教师/管理员）")
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    """创建新课程。"""
    # 检查课程编码是否已存在
    if course_service.get_by_code(db, payload.course_code):
        raise BusinessException("课程编码已存在", code=409)

    # 教师只能创建自己的课程
    data = payload.model_dump()
    if current.role_code == RoleCode.TEACHER.value:
        data["teacher_id"] = current.user_id

    course = course_service.create(db, CourseCreate(**data))
    return success(data=CourseOut.model_validate(course).model_dump(), msg="创建成功")


@router.get("", summary="课程列表")
def list_courses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索关键词（课程名称/编码）"),
    teacher_id: int | None = Query(None, description="教师ID"),
    org_id: int | None = Query(None, description="组织ID"),
    status: int | None = Query(None, description="状态：0-禁用 1-启用 2-结束"),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """获取课程列表，支持搜索和过滤。"""
    offset = (page - 1) * page_size

    # 教师只能查看自己的课程
    if current.role_code == RoleCode.TEACHER.value:
        teacher_id = current.user_id

    items = course_service.list(
        db,
        offset=offset,
        limit=page_size,
        keyword=keyword,
        teacher_id=teacher_id,
        org_id=org_id,
        status=status,
    )
    total = course_service.count(
        db,
        keyword=keyword,
        teacher_id=teacher_id,
        org_id=org_id,
        status=status,
    )

    return success(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [CourseOut.model_validate(c).model_dump() for c in items],
        }
    )


@router.post("/{course_id}/pin", summary="置顶课程")
def pin_course(
    course_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    """将课程置顶（sort_order 设为 -1，排在最前面）。"""
    course = course_service.get(db, course_id)
    if not course or course.is_deleted == 1:
        raise BusinessException("课程不存在", code=404)

    if current.role_code == RoleCode.TEACHER.value and course.teacher_id != current.user_id:
        raise BusinessException("无权操作该课程", code=403)

    course.sort_order = -1
    db.add(course)
    db.commit()
    db.refresh(course)
    return success(data=CourseOut.model_validate(course).model_dump(), msg="置顶成功")


@router.get("/{course_id}", summary="课程详情")
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """获取单个课程详情。"""
    course = course_service.get(db, course_id)
    if not course or course.is_deleted == 1:
        raise BusinessException("课程不存在", code=404)

    # 教师只能查看自己的课程
    if current.role_code == RoleCode.TEACHER.value and course.teacher_id != current.user_id:
        raise BusinessException("无权访问该课程", code=403)

    return success(data=CourseOut.model_validate(course).model_dump())


@router.put("/{course_id}", summary="更新课程（教师/管理员）")
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    """更新课程信息。"""
    course = course_service.get(db, course_id)
    if not course or course.is_deleted == 1:
        raise BusinessException("课程不存在", code=404)

    # 教师只能更新自己的课程
    if current.role_code == RoleCode.TEACHER.value and course.teacher_id != current.user_id:
        raise BusinessException("无权修改该课程", code=403)

    # 教师不能修改课程的归属教师
    update_data = payload.model_dump(exclude_unset=True)
    if current.role_code == RoleCode.TEACHER.value:
        update_data.pop("teacher_id", None)

    course = course_service.update(db, course, CourseUpdate(**update_data))
    return success(data=CourseOut.model_validate(course).model_dump(), msg="更新成功")


@router.delete("/{course_id}", summary="删除课程（教师/管理员）")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.TEACHER, RoleCode.ADMIN)),
):
    """删除课程（软删除）。"""
    course = course_service.get(db, course_id)
    if not course or course.is_deleted == 1:
        raise BusinessException("课程不存在", code=404)

    # 教师只能删除自己的课程
    if current.role_code == RoleCode.TEACHER.value and course.teacher_id != current.user_id:
        raise BusinessException("无权删除该课程", code=403)

    if not course_service.remove(db, course_id):
        raise BusinessException("删除失败", code=500)

    return success(msg="删除成功")
