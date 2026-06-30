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
    Base,
    EvalIndicator,
    Org,
    Role,
    TrainAchievement,
    TrainProject,
    User,
)
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

        project = db.scalar(select(TrainProject).where(TrainProject.project_code == "STE-DEMO-001"))
        if not project:
            project = TrainProject(
                project_name="基于大模型的软件实训智能评价系统",
                project_code="STE-DEMO-001",
                org_id=school_org.id,
                teacher_id=users["teacher"].id,
                enterprise_id=users["enterprise"].id,
                category="软件开发",
                difficulty=2,
                description="完成软件实训成果提交、智能核查、多维度评价和报表导出闭环。",
                status=1,
            )
            db.add(project)
            db.flush()
        else:
            project.teacher_id = users["teacher"].id
            project.enterprise_id = users["enterprise"].id
            project.status = 1

        for index, (code, name, weight, rule) in enumerate(INDICATOR_SEED, start=1):
            indicator = db.scalar(
                select(EvalIndicator).where(
                    EvalIndicator.project_id == project.id,
                    EvalIndicator.indicator_code == code,
                )
            )
            if not indicator:
                db.add(EvalIndicator(
                    project_id=project.id,
                    indicator_code=code,
                    indicator_name=name,
                    weight=weight,
                    max_score=Decimal("100"),
                    scoring_rule=rule,
                    sort=index,
                    status=1,
                ))

        achievement = db.scalar(
            select(TrainAchievement).where(
                TrainAchievement.project_id == project.id,
                TrainAchievement.student_id == users["student"].id,
                TrainAchievement.title == "演示成果提交",
            )
        )
        if not achievement:
            db.add(TrainAchievement(
                project_id=project.id,
                student_id=users["student"].id,
                title="演示成果提交",
                content="已完成项目基础页面、接口联调和评价流程，待教师与企业导师复核。",
                repo_url="https://example.com/demo/smart-train-eval",
                status=1,
                submit_time=datetime.now(timezone.utc),
            ))

        db.commit()

    logger.info("Demo data ready. Accounts: student/teacher/enterprise/admin, password 123456")


if __name__ == "__main__":
    init()
