"""初始化数据库：建表 + 写入基础角色与默认管理员账号。

用法（在 backend 目录下）：
    python -m scripts.init_db
"""
from sqlalchemy import select

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models import Base, Role, User
from app.utils.enums import RoleCode
from app.utils.logger import logger

ROLE_SEED = [
    {"role_name": "学生", "role_code": RoleCode.STUDENT, "data_scope": 1, "sort": 1},
    {"role_name": "教师", "role_code": RoleCode.TEACHER, "data_scope": 2, "sort": 2},
    {"role_name": "企业导师", "role_code": RoleCode.ENTERPRISE, "data_scope": 2, "sort": 3},
    {"role_name": "管理员", "role_code": RoleCode.ADMIN, "data_scope": 3, "sort": 4},
]


def init() -> None:
    logger.info("创建数据表 ...")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # 初始化角色
        for item in ROLE_SEED:
            exists = db.scalar(select(Role).where(Role.role_code == item["role_code"]))
            if not exists:
                db.add(Role(**{**item, "role_code": str(item["role_code"])}))
        db.commit()

        # 初始化默认管理员（admin / admin123）
        admin_role = db.scalar(
            select(Role).where(Role.role_code == RoleCode.ADMIN.value)
        )
        if admin_role and not db.scalar(
            select(User).where(User.username == "admin")
        ):
            db.add(
                User(
                    username="admin",
                    password=hash_password("admin123"),
                    real_name="超级管理员",
                    role_id=admin_role.id,
                    status=1,
                )
            )
            db.commit()
            logger.info("已创建默认管理员：admin / admin123")

    logger.info("数据库初始化完成")


if __name__ == "__main__":
    init()
