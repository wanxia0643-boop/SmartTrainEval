"""Keep course, project, submission, and review work items in sync."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course_enrollment import CourseEnrollment
from app.models.project import TrainProject
from app.services.work_item_service import ensure_work_item


def create_project_submission_tasks(
    db: Session, project: TrainProject, creator_id: int | None = None
) -> int:
    if not project.course_id:
        return 0
    student_ids = db.scalars(select(CourseEnrollment.student_id).where(
        CourseEnrollment.course_id == project.course_id,
        CourseEnrollment.status == 1,
        CourseEnrollment.is_deleted == 0,
    )).all()
    for student_id in student_ids:
        ensure_work_item(
            db,
            assignee_id=student_id,
            creator_id=creator_id,
            task_type="SUBMIT_ACHIEVEMENT",
            biz_type="PROJECT",
            biz_id=project.id,
            title=f"提交实训成果：{project.project_name}",
            description=project.description,
            priority=3,
            due_time=project.end_time,
        )
    return len(student_ids)

