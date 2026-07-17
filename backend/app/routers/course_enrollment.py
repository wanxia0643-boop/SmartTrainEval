"""Course enrollment routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.schemas.auth import CurrentUser
from app.schemas.course import CourseOut
from app.schemas.course_enrollment import CourseEnrollmentCreate, CourseEnrollmentOut
from app.services.course_enrollment_service import course_enrollment_service
from app.services.project_workflow_service import create_project_submission_tasks
from app.models.project import TrainProject
from app.utils.enums import RoleCode

router = APIRouter(prefix="/course-enrollments", tags=["课程选课"])


@router.post("", summary="学生选课（通过课程编码）")
def enroll_course(
    payload: CourseEnrollmentCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.STUDENT)),
):
    """学生通过课程编码加入课程。"""
    # 查找课程
    course = db.query(Course).filter(
        Course.course_code == payload.course_code,
        Course.is_deleted == 0,
        Course.status == 1,
    ).first()

    if not course:
        raise BusinessException("课程不存在或已关闭", code=404)

    # 检查是否已选
    existing = course_enrollment_service.get_by_student_and_course(db, current.user_id, course.id)
    if existing:
        raise BusinessException("你已选择该课程", code=409)

    # 检查人数限制
    if course.max_students:
        current_count = db.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course.id,
            CourseEnrollment.is_deleted == 0,
            CourseEnrollment.status == 1,
        ).count()
        if current_count >= course.max_students:
            raise BusinessException("课程人数已满", code=409)

    enrollment = course_enrollment_service.enroll(db, course.id, current.user_id)
    projects = db.query(TrainProject).filter(
        TrainProject.course_id == course.id,
        TrainProject.status == 1,
        TrainProject.is_deleted == 0,
    ).all()
    for project in projects:
        create_project_submission_tasks(db, project, course.teacher_id)
    db.commit()
    return success(data=CourseEnrollmentOut.model_validate(enrollment).model_dump(), msg="选课成功")


@router.get("", summary="学生已选课程列表")
def list_enrolled_courses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索关键词（课程名称/编码）"),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.STUDENT)),
):
    """获取学生已选课程列表。"""
    offset = (page - 1) * page_size

    # 构建基础查询：学生已选课程
    base_query = db.query(CourseEnrollment).filter(
        CourseEnrollment.student_id == current.user_id,
        CourseEnrollment.is_deleted == 0,
        CourseEnrollment.status == 1,
    )

    # 如果有关键词，需要关联 Course 表进行过滤
    if keyword:
        keyword_pattern = f"%{keyword}%"
        base_query = base_query.join(Course).filter(
            (Course.course_name.like(keyword_pattern)) | (Course.course_code.like(keyword_pattern))
        )

    # 获取总数
    total = base_query.count()

    # 获取分页数据
    enrollments = base_query.offset(offset).limit(page_size).all()

    # 获取课程详情
    course_ids = [e.course_id for e in enrollments]
    courses = db.query(Course).filter(Course.id.in_(course_ids), Course.is_deleted == 0).all()
    course_map = {c.id: c for c in courses}

    items = []
    for e in enrollments:
        course = course_map.get(e.course_id)
        if course:
            items.append({
                "enrollment_id": e.id,
                **CourseOut.model_validate(course).model_dump(),
            })

    return success(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        }
    )


@router.delete("/{enrollment_id}", summary="退课")
def drop_course(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(RoleCode.STUDENT)),
):
    """学生退课。"""
    enrollment = db.get(CourseEnrollment, enrollment_id)
    if not enrollment or enrollment.is_deleted == 1:
        raise BusinessException("选课记录不存在", code=404)

    # 只能退自己的课
    if enrollment.student_id != current.user_id:
        raise BusinessException("无权操作", code=403)

    if not course_enrollment_service.drop(db, enrollment_id):
        raise BusinessException("退课失败", code=500)

    return success(msg="退课成功")
