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
from app.models.course_enrollment import CourseEnrollment
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
