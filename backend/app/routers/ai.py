"""AI-assisted review routes."""
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.evaluator import ai_evaluator
from app.core.access import ensure_achievement_review
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import require_roles
from app.core.response import success
from app.schemas.ai_review import AIReviewRequest
from app.schemas.auth import CurrentUser
from app.services.llm_log_service import llm_log_service
from app.utils.enums import RoleCode
from app.utils.file_extract import extract_text
from app.utils.logger import logger

router = APIRouter(prefix="/ai", tags=["AI智能核查"])

_REVIEW_ROLES = (RoleCode.TEACHER, RoleCode.ENTERPRISE, RoleCode.ADMIN)
_BACKEND_DIR = Path(__file__).resolve().parents[2]


def _fallback_result(reason: str) -> dict:
    return {
        "available": False,
        "function_check": {
            "is_complete": False,
            "problem_list": ["AI 核查未完成，请按指标进行人工复核。"],
        },
        "logic_check": {
            "has_risk": True,
            "risk_list": ["未获得模型输出，暂不能自动判断逻辑风险。"],
        },
        "step_check": {
            "is_complete": False,
            "missing_steps": ["请教师或企业导师根据成果材料补充过程核验。"],
        },
        "standard_score": 0,
        "standard_suggestion": "检查模型配置或网络后可重新发起 AI 核查；人工评分流程不受影响。",
        "summary": reason,
    }


def _local_upload_path(file_url: str | None) -> Path | None:
    if not file_url or not file_url.startswith("/uploads/"):
        return None
    path = (_BACKEND_DIR / file_url.lstrip("/")).resolve()
    try:
        path.relative_to((_BACKEND_DIR / "uploads").resolve())
    except ValueError:
        return None
    return path if path.exists() else None


def _hydrate_from_achievement(
    db: Session,
    payload: AIReviewRequest,
    current: CurrentUser,
) -> tuple[str, str]:
    requirement = (payload.training_requirement or "").strip()
    content = (payload.student_content or "").strip()
    if payload.achievement_id is None:
        return requirement, content

    achievement, project = ensure_achievement_review(db, payload.achievement_id, current)
    if not requirement:
        requirement = project.description or project.project_name
    if not content:
        parts = [achievement.title or "", achievement.content or ""]
        local_path = _local_upload_path(achievement.attachment_url)
        if local_path:
            extracted = extract_text(local_path)
            if extracted:
                parts.append(f"附件解析内容:\n{extracted}")
        if achievement.repo_url:
            parts.append(f"代码仓库: {achievement.repo_url}")
        content = "\n\n".join(p for p in parts if p)
    return requirement, content


@router.post("/review", summary="实训成果智能核查（教师/企业导师/管理员）")
def ai_review(
    payload: AIReviewRequest,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(*_REVIEW_ROLES)),
):
    requirement, content = _hydrate_from_achievement(db, payload, current)
    if not requirement or not content:
        return success(
            data=_fallback_result("缺少实训要求或成果内容，无法发起 AI 核查。"),
            msg="AI 核查未完成",
        )

    try:
        outcome = ai_evaluator.review(requirement, content)
    except Exception as exc:
        logger.exception("AI review failed")
        llm_log_service.create(db, {
            "user_id": current.user_id,
            "biz_type": "ACHIEVEMENT_REVIEW",
            "biz_id": payload.achievement_id,
            "model_name": settings.llm_model or "unknown",
            "status": 0,
            "error_msg": str(exc)[:1000],
        })
        return success(
            data=_fallback_result(f"AI 核查失败：{exc}"),
            msg="AI 核查未完成，已返回人工复核提示",
        )

    llm_log_service.create(db, {
        "user_id": current.user_id,
        "biz_type": "ACHIEVEMENT_REVIEW",
        "biz_id": payload.achievement_id,
        "model_name": outcome.model_name,
        "prompt_text": outcome.prompt_text,
        "response_text": outcome.response_text,
        "prompt_tokens": outcome.prompt_tokens,
        "completion_tokens": outcome.completion_tokens,
        "total_tokens": outcome.total_tokens,
        "duration_ms": outcome.duration_ms,
        "status": 1,
    })
    return success(
        data={**outcome.result.model_dump(), "available": True},
        msg="核查完成",
    )
