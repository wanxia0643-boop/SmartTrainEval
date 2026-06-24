"""AI 智能核查路由。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.evaluator import ai_evaluator
from app.core.database import get_db
from app.core.deps import require_roles
from app.core.exceptions import BusinessException
from app.core.response import success
from app.schemas.ai_review import AIReviewRequest
from app.schemas.auth import CurrentUser
from app.services.llm_log_service import llm_log_service
from app.utils.enums import RoleCode
from app.utils.logger import logger

router = APIRouter(prefix="/ai", tags=["AI智能核查"])

# 可发起 AI 核查的角色
_REVIEW_ROLES = (RoleCode.TEACHER, RoleCode.ENTERPRISE, RoleCode.ADMIN)


@router.post("/review", summary="实训成果智能核查（教师/企业导师/管理员）")
def ai_review(
    payload: AIReviewRequest,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_roles(*_REVIEW_ROLES)),
):
    """调用大模型对成果做结构化核查，并将本次调用记录到 llm_call_log。"""
    try:
        outcome = ai_evaluator.review(payload.training_requirement, payload.student_content)
    except Exception as exc:  # 失败也落库，便于排查与统计
        logger.exception("AI 智能核查失败")
        llm_log_service.create(db, {
            "user_id": current.user_id,
            "biz_type": "ACHIEVEMENT_REVIEW",
            "biz_id": payload.achievement_id,
            "model_name": "unknown",
            "status": 0,
            "error_msg": str(exc)[:1000],
        })
        raise BusinessException(f"AI 智能核查失败: {exc}", code=500) from exc

    # 成功落库
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
    return success(data=outcome.result.model_dump(), msg="核查完成")
