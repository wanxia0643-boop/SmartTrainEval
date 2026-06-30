"""Generate lightweight report files for demo acceptance."""
import csv
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.access import is_admin, is_teacher
from app.models.achievement import TrainAchievement
from app.models.eval_result import EvalResult
from app.models.llm_log import LlmCallLog
from app.models.project import TrainProject
from app.models.user import User
from app.schemas.auth import CurrentUser

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPORT_ROOT = BACKEND_DIR / "generated" / "reports"


def _write_csv(rows: list[dict], prefix: str) -> str:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}.csv"
    path = REPORT_ROOT / filename
    headers = list(rows[0].keys()) if rows else ["message"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        if rows:
            writer.writerows(rows)
        else:
            writer.writerow({"message": "暂无数据"})
    return f"/generated/reports/{filename}"


def _achievement_query(db: Session, current: CurrentUser, project_id: int | None):
    stmt = (
        select(TrainAchievement, TrainProject, User)
        .join(TrainProject, TrainAchievement.project_id == TrainProject.id)
        .outerjoin(User, TrainAchievement.student_id == User.id)
        .where(
            TrainAchievement.is_deleted == 0,
            TrainProject.is_deleted == 0,
        )
        .order_by(TrainAchievement.id.desc())
    )
    if project_id is not None:
        stmt = stmt.where(TrainAchievement.project_id == project_id)
    if is_teacher(current):
        stmt = stmt.where(TrainProject.teacher_id == current.user_id)
    return db.execute(stmt).all()


def generate_report_file(
    db: Session,
    *,
    report_type: int,
    project_id: int | None,
    current: CurrentUser,
) -> str:
    """Generate a CSV report and return its public file URL."""
    if report_type in (1, 2, 3):
        rows = []
        for achievement, project, student in _achievement_query(db, current, project_id):
            rows.append({
                "项目": project.project_name,
                "项目编码": project.project_code,
                "学生": student.real_name if student else achievement.student_id,
                "成果标题": achievement.title,
                "状态": achievement.status,
                "最终得分": achievement.final_score if achievement.final_score is not None else "",
                "提交时间": achievement.submit_time or achievement.create_time,
            })
        return _write_csv(rows, "achievement-report")

    if report_type == 4:
        stmt = select(LlmCallLog).where(LlmCallLog.is_deleted == 0).order_by(LlmCallLog.id.desc())
        if not is_admin(current):
            stmt = stmt.where(LlmCallLog.user_id == current.user_id)
        logs = db.scalars(stmt.limit(500)).all()
        rows = [{
            "业务类型": log.biz_type or "",
            "业务ID": log.biz_id or "",
            "模型": log.model_name,
            "状态": "成功" if log.status == 1 else "失败",
            "Token": log.total_tokens,
            "耗时ms": log.duration_ms,
            "错误": log.error_msg or "",
            "时间": log.create_time,
        } for log in logs]
        return _write_csv(rows, "ai-usage-report")

    return _write_csv([], "empty-report")
