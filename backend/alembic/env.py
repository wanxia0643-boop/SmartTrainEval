"""Alembic 迁移环境。

从应用配置读取数据库连接串，从 app.models.Base 读取元数据，
以支持 `alembic revision --autogenerate`。
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings

# 导入 Base 并触发所有模型注册（models/__init__ 已汇总导入全部模型）
from app.models import Base  # noqa: F401  确保 metadata 收集到所有表
import app.models  # noqa: F401

# Alembic Config 对象
config = context.config

# 注入数据库连接串（避免在 alembic.ini 明文存放密码）
config.set_main_option("sqlalchemy.url", settings.database_url)

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 的目标元数据
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式：仅生成 SQL，不连接数据库。"""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：连接数据库执行迁移。"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,            # 检测字段类型变化
            compare_server_default=True,  # 检测默认值变化
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
