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

# 演示账号：与前端登录页对应，密码统一 123456
USER_SEED = [
    {"username": "student", "real_name": "林晓", "role_code": RoleCode.STUDENT},
    {"username": "teacher", "real_name": "张老师", "role_code": RoleCode.TEACHER},
    {"username": "enterprise", "real_name": "陈导师", "role_code": RoleCode.ENTERPRISE},
    {"username": "admin", "real_name": "系统管理员", "role_code": RoleCode.ADMIN},
]
DEFAULT_PASSWORD = "123456"


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

        # 角色编码 -> 角色ID 映射
        role_id_by_code = {
            r.role_code: r.id for r in db.scalars(select(Role)).all()
        }

        # 初始化演示账号（已存在则跳过）
        for item in USER_SEED:
            if db.scalar(select(User).where(User.username == item["username"])):
                continue
            role_id = role_id_by_code.get(str(item["role_code"]))
            if not role_id:
                continue
            db.add(
                User(
                    username=item["username"],
                    password=hash_password(DEFAULT_PASSWORD),
                    real_name=item["real_name"],
                    role_id=role_id,
                    status=1,
                )
            )
            logger.info(f"已创建演示账号：{item['username']} / {DEFAULT_PASSWORD}")
        db.commit()

    logger.info("数据库初始化完成")


if __name__ == "__main__":
    init()
