"""Initialize database schema and stable demo data.

Run from backend/:
    python -m scripts.init_db
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    AIAnalysis,
    Base,
    Course,
    CourseEnrollment,
    EvalIndicator,
    EvalResult,
    KnowledgeChunk,
    KnowledgeDocument,
    Org,
    Role,
    TrainAchievement,
    TrainProject,
    User,
    WorkItem,
)
from app.services.project_workflow_service import create_project_submission_tasks
from app.services.eval_result_service import eval_result_service
from app.services.work_item_service import complete_work_items, ensure_work_item
from app.utils.enums import RoleCode
from app.utils.logger import logger

DEFAULT_PASSWORD = "123456"

ROLE_SEED = [
    {"role_name": "学生", "role_code": RoleCode.STUDENT.value, "data_scope": 1, "sort": 1},
    {"role_name": "教师", "role_code": RoleCode.TEACHER.value, "data_scope": 2, "sort": 2},
    {"role_name": "企业导师", "role_code": RoleCode.ENTERPRISE.value, "data_scope": 2, "sort": 3},
    {"role_name": "管理员", "role_code": RoleCode.ADMIN.value, "data_scope": 3, "sort": 4},
]

USER_SEED = [
    {"username": "student", "real_name": "林晓", "role_code": RoleCode.STUDENT.value, "student_no": "ST2026001"},
    {"username": "student02", "real_name": "周然", "role_code": RoleCode.STUDENT.value, "student_no": "ST2026002"},
    {"username": "student03", "real_name": "苏晴", "role_code": RoleCode.STUDENT.value, "student_no": "ST2026003"},
    {"username": "student04", "real_name": "陈宇", "role_code": RoleCode.STUDENT.value, "student_no": "ST2026004"},
    {"username": "student05", "real_name": "许诺", "role_code": RoleCode.STUDENT.value, "student_no": "ST2026005"},
    {"username": "student06", "real_name": "唐可", "role_code": RoleCode.STUDENT.value, "student_no": "ST2026006"},
    {"username": "student07", "real_name": "方圆", "role_code": RoleCode.STUDENT.value, "student_no": "ST2026007"},
    {"username": "student08", "real_name": "韩睿", "role_code": RoleCode.STUDENT.value, "student_no": "ST2026008"},
    {"username": "teacher", "real_name": "张老师", "role_code": RoleCode.TEACHER.value, "student_no": "T2026001"},
    {"username": "enterprise", "real_name": "陈导师", "role_code": RoleCode.ENTERPRISE.value, "student_no": "E2026001"},
    {"username": "admin", "real_name": "系统管理员", "role_code": RoleCode.ADMIN.value, "student_no": "A2026001"},
]

ORG_SEED = [
    {"org_name": "示范软件学院", "org_code": "DEMO-SCHOOL", "org_type": 1, "sort": 1},
    {"org_name": "龙芯中科技术股份有限公司", "org_code": "DEMO-ENT", "org_type": 5, "sort": 2},
]

INDICATOR_SEED = [
    ("REQ", "需求完成度", Decimal("30"), "功能点覆盖实训要求，核心流程可运行。"),
    ("CODE", "代码质量", Decimal("25"), "结构清晰，命名规范，异常处理完整。"),
    ("PROCESS", "过程完整性", Decimal("25"), "提交材料能体现设计、实现、测试和迭代过程。"),
    ("DOC", "文档与表达", Decimal("20"), "报告结构完整，截图和结论可支撑评价。"),
]


def _get_or_create_role(db, item):
    obj = db.scalar(select(Role).where(Role.role_code == item["role_code"]))
    if obj:
        return obj
    obj = Role(**item)
    db.add(obj)
    db.flush()
    return obj


def _get_or_create_org(db, item):
    obj = db.scalar(select(Org).where(Org.org_code == item["org_code"]))
    if obj:
        return obj
    obj = Org(**item)
    db.add(obj)
    db.flush()
    return obj


def _get_or_create_user(db, item, role_id, org_id):
    obj = db.scalar(select(User).where(User.username == item["username"]))
    if obj:
        obj.role_id = role_id
        obj.org_id = org_id
        obj.password = hash_password(DEFAULT_PASSWORD)
        obj.real_name = item["real_name"]
        obj.student_no = item.get("student_no")
        obj.status = 1
        return obj
    obj = User(
        username=item["username"],
        password=hash_password(DEFAULT_PASSWORD),
        real_name=item["real_name"],
        role_id=role_id,
        org_id=org_id,
        student_no=item.get("student_no"),
        status=1,
    )
    db.add(obj)
    db.flush()
    return obj


def init() -> None:
    logger.info("Creating tables and demo data...")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        roles = {item["role_code"]: _get_or_create_role(db, item) for item in ROLE_SEED}
        orgs = [_get_or_create_org(db, item) for item in ORG_SEED]
        school_org, enterprise_org = orgs[0], orgs[1]

        users = {}
        for item in USER_SEED:
            org_id = enterprise_org.id if item["role_code"] == RoleCode.ENTERPRISE.value else school_org.id
            users[item["username"]] = _get_or_create_user(
                db,
                item,
                roles[item["role_code"]].id,
                org_id,
            )

        course = db.scalar(select(Course).where(Course.course_code == "STE-COURSE-2026"))
        if not course:
            course = Course(
                course_name="软件工程综合实训",
                course_code="STE-COURSE-2026",
                teacher_id=users["teacher"].id,
                org_id=school_org.id,
                category="软件工程",
                description="以真实项目为载体，训练需求、设计、开发、测试与汇报能力。",
                status=1,
                max_students=40,
                credits=4,
            )
            db.add(course)
            db.flush()
        else:
            course.teacher_id = users["teacher"].id
            course.status = 1

        student_users = [users["student"]] + [users[f"student{i:02d}"] for i in range(2, 9)]
        for student_user in student_users:
            enrollment = db.scalar(select(CourseEnrollment).where(
                CourseEnrollment.course_id == course.id,
                CourseEnrollment.student_id == student_user.id,
                CourseEnrollment.is_deleted == 0,
            ))
            if not enrollment:
                db.add(CourseEnrollment(course_id=course.id, student_id=student_user.id, status=1))
            else:
                enrollment.status = 1
        db.flush()

        project_specs = [
            ("STE-DEMO-001", "AI 实训智能评价平台", 1, "完成课程、项目、成果、多主体评价、AI辅导和报告展示闭环。"),
            ("STE-DEMO-000", "软件需求与原型迭代", 2, "围绕真实需求完成用户分析、原型设计、可用性验证和迭代报告。"),
        ]
        projects = []
        for code, name, status, description in project_specs:
            project = db.scalar(select(TrainProject).where(TrainProject.project_code == code))
            if not project:
                project = TrainProject(
                    project_name=name,
                    project_code=code,
                    org_id=school_org.id,
                    course_id=course.id,
                    teacher_id=users["teacher"].id,
                    enterprise_id=users["enterprise"].id,
                    category="软件开发",
                    difficulty=2,
                    description=description,
                    status=status,
                )
                db.add(project)
                db.flush()
            else:
                project.course_id = course.id
                project.teacher_id = users["teacher"].id
                project.enterprise_id = users["enterprise"].id
                project.status = status
            projects.append(project)

        indicator_maps = {}
        for project in projects:
            indicator_maps[project.id] = []
            for index, (code, name, weight, rule) in enumerate(INDICATOR_SEED, start=1):
                indicator = db.scalar(select(EvalIndicator).where(
                    EvalIndicator.project_id == project.id,
                    EvalIndicator.indicator_code == code,
                    EvalIndicator.is_deleted == 0,
                ))
                if not indicator:
                    indicator = EvalIndicator(
                        project_id=project.id,
                        indicator_code=code,
                        indicator_name=name,
                        weight=weight,
                        max_score=Decimal("100"),
                        scoring_rule=rule,
                        sort=index,
                        status=1,
                    )
                    db.add(indicator)
                    db.flush()
                indicator_maps[project.id].append(indicator)

        current_project, previous_project = projects
        current_statuses = [1, 2, 4, 3, 3, 3, 3, 3]
        for project_index, project in enumerate(projects):
            for index, student_user in enumerate(student_users):
                title = f"{student_user.real_name} · {project.project_name}成果"
                achievement = db.scalar(select(TrainAchievement).where(
                    TrainAchievement.project_id == project.id,
                    TrainAchievement.student_id == student_user.id,
                    TrainAchievement.title == title,
                    TrainAchievement.is_deleted == 0,
                ))
                target_status = current_statuses[index] if project == current_project else 3
                base_score = 72 + index * 3 + project_index * 2
                if not achievement:
                    achievement = TrainAchievement(
                        project_id=project.id,
                        student_id=student_user.id,
                        title=title,
                        content="已完成需求分析、核心功能实现、接口联调与测试，并整理关键过程证据。",
                        repo_url=f"https://example.com/demo/{project.project_code.lower()}/{student_user.username}",
                        status=target_status,
                        final_score=Decimal(str(min(base_score, 96))) if target_status == 3 else None,
                        submit_time=datetime.now(timezone.utc),
                    )
                    db.add(achievement)
                    db.flush()
                else:
                    achievement.status = target_status
                    achievement.final_score = Decimal(str(min(base_score, 96))) if target_status == 3 else None

                if target_status == 3:
                    for eval_type, evaluator_key, offset in ((2, "teacher", 1), (3, "enterprise", -1)):
                        for indicator in indicator_maps[project.id]:
                            existing = db.scalar(select(EvalResult).where(
                                EvalResult.achievement_id == achievement.id,
                                EvalResult.indicator_id == indicator.id,
                                EvalResult.eval_type == eval_type,
                                EvalResult.is_deleted == 0,
                            ))
                            if not existing:
                                db.add(EvalResult(
                                    achievement_id=achievement.id,
                                    indicator_id=indicator.id,
                                    eval_type=eval_type,
                                    evaluator_id=users[evaluator_key].id,
                                    score=Decimal(str(min(base_score + offset, 98))),
                                    comment="核心流程完成，工程结构清晰。",
                                    suggestion="继续补强自动化测试与过程证据。",
                                    eval_time=datetime.now(timezone.utc),
                                ))

        document = db.scalar(select(KnowledgeDocument).where(
            KnowledgeDocument.course_id == course.id,
            KnowledgeDocument.title == "软件实训课程规范",
            KnowledgeDocument.is_deleted == 0,
        ))
        if not document:
            document = KnowledgeDocument(
                course_id=course.id,
                uploader_id=users["teacher"].id,
                title="软件实训课程规范",
                file_name="demo-training-guide.md",
                file_url="/generated/demo-training-guide.md",
                mime_type="text/markdown",
                status=1,
            )
            db.add(document)
            db.flush()
            chunks = [
                "成果必须覆盖需求分析、技术方案、核心实现、测试验证和迭代复盘。每项结论都应有代码、截图、测试记录或文档作为证据。",
                "提交前应确认主流程可运行、异常输入有处理、仓库或附件可访问，并在报告中说明关键技术决策与测试结果。",
                "AI仅用于启发式辅导和预检，不直接计入成绩。最终成绩由教师评价百分之六十与企业导师评价百分之四十组成。",
            ]
            for index, content in enumerate(chunks):
                db.add(KnowledgeChunk(document_id=document.id, chunk_index=index, source_label=f"课程规范第 {index + 1} 节", content=content))

        create_project_submission_tasks(db, current_project, users["teacher"].id)
        for achievement in db.scalars(select(TrainAchievement).where(
            TrainAchievement.project_id == current_project.id,
            TrainAchievement.is_deleted == 0,
        )).all():
            complete_work_items(db, assignee_id=achievement.student_id, biz_type="PROJECT", biz_id=current_project.id)
            if achievement.status in (1, 2):
                ensure_work_item(db, assignee_id=users["teacher"].id, task_type="TEACHER_REVIEW", biz_type="ACHIEVEMENT", biz_id=achievement.id, title=f"教师评价：{achievement.title}", priority=3)
                ensure_work_item(db, assignee_id=users["enterprise"].id, task_type="ENTERPRISE_REVIEW", biz_type="ACHIEVEMENT", biz_id=achievement.id, title=f"企业评价：{achievement.title}", priority=2)
            elif achievement.status == 4:
                ensure_work_item(db, assignee_id=achievement.student_id, task_type="REDO_ACHIEVEMENT", biz_type="ACHIEVEMENT", biz_id=achievement.id, title=f"整改并重新提交：{achievement.title}", priority=3)
            elif achievement.status == 3:
                ensure_work_item(db, assignee_id=achievement.student_id, task_type="VIEW_FEEDBACK", biz_type="ACHIEVEMENT", biz_id=achievement.id, title=f"查看评价反馈：{achievement.title}", priority=2)

        db.flush()
        evaluated_achievements = list(db.scalars(select(TrainAchievement).where(
            TrainAchievement.status == 3,
            TrainAchievement.project_id.in_([item.id for item in projects]),
            TrainAchievement.is_deleted == 0,
        )).all())
        for achievement in evaluated_achievements:
            eval_result_service.recalc_final_score(db, achievement.id)
            ensure_work_item(
                db, assignee_id=achievement.student_id, task_type="VIEW_FEEDBACK",
                biz_type="ACHIEVEMENT", biz_id=achievement.id,
                title=f"查看评价反馈：{achievement.title}", priority=1,
            )

        db.commit()

    logger.info("Demo data ready. Accounts: student/student02..student08/teacher/enterprise/admin, password 123456")


if __name__ == "__main__":
    init()
