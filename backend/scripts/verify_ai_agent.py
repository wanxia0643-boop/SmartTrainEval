"""Repeatable smoke test for the four-role AI training workflow.

Run while the backend is listening on 127.0.0.1:8000:
    python -m scripts.verify_ai_agent
"""
import json
import os

import requests
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.achievement import TrainAchievement
from app.models.ai_agent import AIAnalysis
from app.models.course_enrollment import CourseEnrollment
from app.models.indicator import EvalIndicator
from app.models.project import TrainProject
from app.models.user import User

BASE_URL = os.getenv("STE_API_BASE", "http://127.0.0.1:8000/api/v1")


def login(username: str) -> str:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": "123456"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["data"]["access_token"]


def call(token: str, method: str, path: str, **kwargs):
    response = requests.request(
        method,
        f"{BASE_URL}{path}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=40,
        **kwargs,
    )
    response.raise_for_status()
    body = response.json()
    assert body["code"] == 0, body
    return body["data"]


def main() -> None:
    tokens = {role: login(role) for role in ("student", "teacher", "enterprise", "admin")}
    projects = call(tokens["student"], "GET", "/projects?page=1&page_size=100")["items"]
    assert projects and all(project["course_id"] for project in projects)
    active = next(project for project in projects if project["project_code"] == "STE-DEMO-001")
    previous = next(project for project in projects if project["project_code"] == "STE-DEMO-000")
    current_achievements = call(
        tokens["student"], "GET", f"/achievements?project_id={active['id']}&page=1&page_size=100"
    )["items"]
    previous_achievement = call(
        tokens["student"], "GET", f"/achievements?project_id={previous['id']}&page=1&page_size=100"
    )["items"][0]
    coach = call(tokens["student"], "POST", "/ai/coach/chat", json={
        "course_id": active["course_id"],
        "achievement_id": current_achievements[0]["id"],
        "project_id": active["id"],
        "message": "提交前应该重点检查哪些材料？",
    })
    assert coach["citations"]
    assert coach["available"] is True
    precheck = call(
        tokens["student"], "POST", f"/ai/achievements/{current_achievements[0]['id']}/precheck"
    )
    assert precheck["next_actions"]
    assert precheck["citations"]
    assert precheck["context_summary"]["indicator_count"] > 0

    project_draft = call(tokens["teacher"], "POST", "/ai/projects/draft", json={
        "course_id": active["course_id"],
        "objective": "设计一个包含需求、实现、测试与复盘证据的两周软件实训项目",
        "difficulty": 2,
        "duration_days": 14,
    })
    assert project_draft["project_name"]
    assert project_draft["milestones"]
    draft_code = f"AI-SMOKE-{project_draft['analysis_id']}"
    edited_indicators = [
        {"name": "需求完成度", "weight": 30, "rule": "核心流程覆盖目标并可运行"},
        {"name": "工程质量", "weight": 25, "rule": "结构清晰且异常处理完整"},
        {"name": "测试证据", "weight": 25, "rule": "测试范围、结果与结论可追溯"},
        {"name": "复盘表达", "weight": 20, "rule": "技术决策和迭代改进有证据支撑"},
    ]
    apply_payload = {
        "analysis_id": project_draft["analysis_id"],
        "course_id": active["course_id"],
        "project_name": project_draft["project_name"],
        "project_code": draft_code,
        "category": "软件开发",
        "difficulty": 2,
        "duration_days": 14,
        "description": project_draft["description"],
        "milestones": project_draft["milestones"],
        "submission_requirements": project_draft["submission_requirements"],
        "indicators": edited_indicators,
    }
    invalid_apply = requests.post(
        f"{BASE_URL}/ai/projects/draft/apply",
        headers={"Authorization": f"Bearer {tokens['teacher']}"},
        json={**apply_payload, "indicators": [{**edited_indicators[0], "weight": 20}, *edited_indicators[1:]]},
        timeout=10,
    )
    assert invalid_apply.status_code == 422
    applied_draft = call(tokens["teacher"], "POST", "/ai/projects/draft/apply", json=apply_payload)
    created_project_id = applied_draft["project"]["id"]
    try:
        assert applied_draft["project"]["status"] == 0
        assert applied_draft["weight_total"] == 100
        assert len(applied_draft["indicators"]) == 4
        teacher_projects = call(tokens["teacher"], "GET", "/projects?page=1&page_size=100")["items"]
        assert any(item["id"] == created_project_id for item in teacher_projects)
        student_projects_after_apply = call(tokens["student"], "GET", "/projects?page=1&page_size=100")["items"]
        assert all(item["id"] != created_project_id for item in student_projects_after_apply)
        hidden_draft = requests.get(
            f"{BASE_URL}/projects/{created_project_id}",
            headers={"Authorization": f"Bearer {tokens['student']}"},
            timeout=10,
        )
        assert hidden_draft.status_code == 403
        duplicate_apply = requests.post(
            f"{BASE_URL}/ai/projects/draft/apply",
            headers={"Authorization": f"Bearer {tokens['teacher']}"},
            json={**apply_payload, "project_code": f"{draft_code}-COPY"},
            timeout=10,
        )
        assert duplicate_apply.status_code == 409
    finally:
        with SessionLocal() as db:
            for indicator in db.scalars(select(EvalIndicator).where(
                EvalIndicator.project_id == created_project_id
            )).all():
                db.delete(indicator)
            created_project = db.get(TrainProject, created_project_id)
            if created_project:
                db.delete(created_project)
            analysis = db.get(AIAnalysis, project_draft["analysis_id"])
            if analysis:
                analysis.biz_type = "COURSE"
                analysis.biz_id = active["course_id"]
                db.add(analysis)
            db.commit()
    class_result = call(tokens["teacher"], "POST", f"/ai/projects/{active['id']}/class-analysis")
    assert class_result["summary"]
    enterprise_achievements = call(
        tokens["enterprise"], "GET", f"/achievements?project_id={active['id']}&page=1&page_size=100"
    )["items"]
    evidence = call(
        tokens["enterprise"], "POST",
        f"/ai/achievements/{enterprise_achievements[0]['id']}/enterprise-evidence",
    )
    assert evidence["competencies"]
    assert evidence["context_summary"]["indicator_count"] > 0
    assert evidence["citations"]
    briefing = call(tokens["enterprise"], "POST", f"/ai/projects/{active['id']}/briefing")
    assert briefing["script"]
    health = call(tokens["admin"], "GET", "/ai/health")
    assert health["scene_stats"]
    assert len(health["daily_calls"]) == 7
    assert "evaluation_completion_rate" in health["process_health"]
    assert "ready" in health["knowledge_status"]

    governance_blocked = requests.get(
        f"{BASE_URL}/ai/health",
        headers={"Authorization": f"Bearer {tokens['teacher']}"},
        timeout=10,
    )
    assert governance_blocked.status_code == 403

    blocked = requests.post(
        f"{BASE_URL}/eval-results",
        headers={"Authorization": f"Bearer {tokens['admin']}"},
        json={"achievement_id": current_achievements[0]["id"], "indicator_id": 1, "score": 90},
        timeout=10,
    )
    assert blocked.status_code == 403

    outsider_token = login("student08")
    outsider_precheck = requests.post(
        f"{BASE_URL}/ai/achievements/{current_achievements[0]['id']}/precheck",
        headers={"Authorization": f"Bearer {outsider_token}"},
        timeout=10,
    )
    assert outsider_precheck.status_code == 403
    with SessionLocal() as db:
        outsider = db.scalar(select(User).where(User.username == "student08"))
        enrollment = db.scalar(select(CourseEnrollment).where(
            CourseEnrollment.student_id == outsider.id,
            CourseEnrollment.course_id == active["course_id"],
            CourseEnrollment.is_deleted == 0,
        ))
        original_status = enrollment.status
        try:
            enrollment.status = 2
            db.add(enrollment)
            db.commit()
            forbidden = requests.get(
                f"{BASE_URL}/projects/{active['id']}",
                headers={"Authorization": f"Bearer {outsider_token}"},
                timeout=10,
            )
            assert forbidden.status_code == 403
        finally:
            enrollment.status = original_status
            db.add(enrollment)
            db.commit()

    teacher_tasks_before = call(tokens["teacher"], "GET", "/work-items?status=0")["total"]
    enterprise_tasks_before = call(tokens["enterprise"], "GET", "/work-items?status=0")["total"]
    draft = call(tokens["student"], "POST", "/achievements", json={
        "project_id": active["id"],
        "student_id": 0,
        "title": "AI workflow smoke-test draft",
        "content": "Temporary evidence draft used by the repeatable workflow smoke test.",
        "status": 0,
    })
    assert draft["status"] == 0
    assert draft["submit_time"] is None
    assert call(tokens["teacher"], "GET", "/work-items?status=0")["total"] == teacher_tasks_before
    assert call(tokens["enterprise"], "GET", "/work-items?status=0")["total"] == enterprise_tasks_before
    call(tokens["admin"], "DELETE", f"/achievements/{draft['id']}")
    with SessionLocal() as db:
        stored_draft = db.get(TrainAchievement, draft["id"])
        if stored_draft:
            db.delete(stored_draft)
            db.commit()

    result = {
        "roles_logged_in": len(tokens),
        "student_projects": len(projects),
        "student_pending_tasks": call(tokens["student"], "GET", "/work-items?status=0")["total"],
        "knowledge_citations": len(coach["citations"]),
        "score_60_40": float(previous_achievement["final_score"]),
        "admin_scoring_blocked": blocked.status_code,
        "unenrolled_project_blocked": forbidden.status_code,
        "other_student_precheck_blocked": outsider_precheck.status_code,
        "draft_created_without_review_tasks": True,
        "ai_project_draft_applied": 4,
        "unpublished_project_hidden": hidden_draft.status_code,
        "duplicate_draft_apply_blocked": duplicate_apply.status_code,
        "enterprise_competencies": len(evidence["competencies"]),
        "enterprise_evidence_sources": len(evidence["citations"]),
        "ai_calls_audited": health["total_calls"],
        "governance_teacher_blocked": governance_blocked.status_code,
        "governance_alerts": len(health["alerts"]),
    }
    assert abs(result["score_60_40"] - 74.2) < 0.01
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
