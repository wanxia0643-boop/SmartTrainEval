"""课程业务逻辑。"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate


class CourseService:
    """Course service."""

    def create(self, db: Session, data: CourseCreate) -> Course:
        """创建课程。"""
        course = Course(**data.model_dump())
        db.add(course)
        db.commit()
        db.refresh(course)
        return course

    def get(self, db: Session, course_id: int) -> Course | None:
        """获取单个课程。"""
        return db.get(Course, course_id)

    def list(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 10,
        keyword: str | None = None,
        teacher_id: int | None = None,
        org_id: int | None = None,
        status: int | None = None,
    ) -> list[Course]:
        """获取课程列表。"""
        stmt = select(Course).where(Course.is_deleted == 0)

        if keyword:
            keyword_pattern = f"%{keyword}%"
            stmt = stmt.where(
                (Course.course_name.like(keyword_pattern))
                | (Course.course_code.like(keyword_pattern))
            )
        if teacher_id is not None:
            stmt = stmt.where(Course.teacher_id == teacher_id)
        if org_id is not None:
            stmt = stmt.where(Course.org_id == org_id)
        if status is not None:
            stmt = stmt.where(Course.status == status)

        stmt = stmt.order_by(Course.sort_order.asc(), Course.id.desc()).offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    def count(
        self,
        db: Session,
        keyword: str | None = None,
        teacher_id: int | None = None,
        org_id: int | None = None,
        status: int | None = None,
    ) -> int:
        """统计课程数量。"""
        stmt = select(func.count()).select_from(Course).where(Course.is_deleted == 0)

        if keyword:
            keyword_pattern = f"%{keyword}%"
            stmt = stmt.where(
                (Course.course_name.like(keyword_pattern))
                | (Course.course_code.like(keyword_pattern))
            )
        if teacher_id is not None:
            stmt = stmt.where(Course.teacher_id == teacher_id)
        if org_id is not None:
            stmt = stmt.where(Course.org_id == org_id)
        if status is not None:
            stmt = stmt.where(Course.status == status)

        return db.scalar(stmt) or 0

    def update(self, db: Session, course: Course, data: CourseUpdate) -> Course:
        """更新课程。"""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)
        db.add(course)
        db.commit()
        db.refresh(course)
        return course

    def remove(self, db: Session, course_id: int) -> bool:
        """删除课程（软删除）。"""
        course = db.get(Course, course_id)
        if not course or course.is_deleted == 1:
            return False
        course.is_deleted = 1
        db.add(course)
        db.commit()
        return True

    def get_by_code(self, db: Session, course_code: str) -> Course | None:
        """根据课程编码获取课程。"""
        stmt = select(Course).where(
            Course.course_code == course_code, Course.is_deleted == 0
        )
        return db.scalars(stmt).first()


course_service = CourseService()
