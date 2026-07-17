"""Shared structured AI invocation with traceable fallback results."""
import json
import re
import time
from typing import Any

from sqlalchemy.orm import Session

from app.ai.llm import get_llm
from app.core.config import settings
from app.models.ai_agent import AIAnalysis
from app.models.llm_log import LlmCallLog


def _extract_json(text: str) -> dict[str, Any]:
    value = text.strip()
    if value.startswith("```"):
        value = re.sub(r"^```[a-zA-Z]*\n?", "", value)
        value = re.sub(r"\n?```$", "", value).strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", value, re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def invoke_structured(
    db: Session,
    *,
    current_user_id: int,
    scene: str,
    biz_type: str,
    biz_id: int | None,
    prompt: str,
    fallback: dict[str, Any],
    citations: list[dict] | None = None,
) -> tuple[dict[str, Any], bool, AIAnalysis]:
    llm = get_llm()
    started = time.perf_counter()
    available = False
    model_name = settings.llm_model or "unconfigured"
    response_text = ""
    result = fallback
    status = 0
    error_msg = None
    usage: dict[str, Any] = {}
    if llm is None:
        error_msg = "大模型未配置，已返回规则化建议"
    else:
        try:
            response = llm.invoke(prompt)
            response_text = getattr(response, "content", str(response))
            response_text = response_text if isinstance(response_text, str) else str(response_text)
            result = _extract_json(response_text)
            usage = getattr(response, "usage_metadata", None) or {}
            available = True
            status = 1
        except Exception as exc:
            error_msg = str(exc)[:1000]
    duration_ms = int((time.perf_counter() - started) * 1000)
    log = LlmCallLog(
        user_id=current_user_id,
        biz_type=scene,
        biz_id=biz_id,
        model_name=model_name,
        prompt_text=prompt,
        response_text=response_text or json.dumps(result, ensure_ascii=False),
        prompt_tokens=usage.get("input_tokens", 0),
        completion_tokens=usage.get("output_tokens", 0),
        total_tokens=usage.get("total_tokens", 0),
        duration_ms=duration_ms,
        status=status,
        error_msg=error_msg,
    )
    db.add(log)
    db.flush()
    analysis = AIAnalysis(
        user_id=current_user_id,
        scene=scene,
        biz_type=biz_type,
        biz_id=biz_id,
        status=status,
        result_json=json.dumps(result, ensure_ascii=False),
        citations_json=json.dumps(citations or [], ensure_ascii=False),
        model_name=model_name,
        prompt_version="v1",
        llm_log_id=log.id,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return result, available, analysis

