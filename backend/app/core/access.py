"""Role-aware access helpers for the demo business workflow."""
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, PermissionException
from app.models.achievement import TrainAchievement
from app.models.project import TrainProject
from app.schemas.auth import CurrentUser
from app.utils.enums import RoleCode


def _role(user: CurrentUser) -> str:
    return str(user.role_code or "")


def is_admin(user: CurrentUser) -> bool:
    return _role(user) == RoleCode.ADMIN.value


def is_teacher(user: CurrentUser) -> bool:
    return _role(user) == RoleCode.TEACHER.value


def is_enterprise(user: CurrentUser) -> bool:
    return _role(user) == RoleCode.ENTERPRISE.value


def is_student(user: CurrentUser) -> bool:
    return _role(user) == RoleCode.STUDENT.value


def get_project_or_404(db: Session, project_id: int) -> TrainProject:
    project = db.get(TrainProject, project_id)
    if not project or project.is_deleted == 1:
        raise BusinessException("项目不存在", code=404)
    return project


def get_achievement_or_404(db: Session, achievement_id: int) -> TrainAchievement:
    achievement = db.get(TrainAchievement, achievement_id)
    if not achievement or achievement.is_deleted == 1:
        raise BusinessException("成果不存在", code=404)
    return achievement


def can_read_project(project: TrainProject, user: CurrentUser) -> bool:
    if is_admin(user):
        return True
    if is_teacher(user):
        return project.teacher_id == user.user_id
    if is_enterprise(user):
        return project.enterprise_id == user.user_id
    if is_student(user):
        return project.status != 3
    return False


def ensure_project_read(db: Session, project_id: int, user: CurrentUser) -> TrainProject:
    project = get_project_or_404(db, project_id)
    if not can_read_project(project, user):
        raise PermissionException("无权访问该项目")
    return project


def ensure_project_write(db: Session, project_id: int, user: CurrentUser) -> TrainProject:
    project = get_project_or_404(db, project_id)
    if is_admin(user) or (is_teacher(user) and project.teacher_id == user.user_id):
        return project
    raise PermissionException("无权维护该项目")


def can_read_achievement(
    achievement: TrainAchievement,
    project: TrainProject,
    user: CurrentUser,
) -> bool:
    if is_admin(user):
        return True
    if is_student(user):
        return achievement.student_id == user.user_id
    if is_teacher(user):
        return project.teacher_id == user.user_id
    if is_enterprise(user):
        return project.enterprise_id == user.user_id
    return False


def ensure_achievement_read(
    db: Session,
    achievement_id: int,
    user: CurrentUser,
) -> tuple[TrainAchievement, TrainProject]:
    achievement = get_achievement_or_404(db, achievement_id)
    project = get_project_or_404(db, achievement.project_id)
    if not can_read_achievement(achievement, project, user):
        raise PermissionException("无权访问该成果")
    return achievement, project


def ensure_achievement_review(
    db: Session,
    achievement_id: int,
    user: CurrentUser,
) -> tuple[TrainAchievement, TrainProject]:
    achievement, project = ensure_achievement_read(db, achievement_id, user)
    if is_admin(user):
        return achievement, project
    if is_teacher(user) and project.teacher_id == user.user_id:
        return achievement, project
    if is_enterprise(user) and project.enterprise_id == user.user_id:
        return achievement, project
    raise PermissionException("无权评价该成果")
