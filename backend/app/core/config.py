"""全局配置：从环境变量 / .env 读取并集中管理。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置项，字段名与 .env 中的变量名（不区分大小写）对应。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用
    app_name: str = "SmartTrainEval"
    app_env: str = "dev"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # 数据库
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "beyond"
    db_password: str = "7454088"
    db_name: str = "smart_train_eval"
    db_echo: bool = False

    # JWT
    jwt_secret_key: str = "please-change-this-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 720

    # 大模型
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_temperature: float = 0.2

    @property
    def database_url(self) -> str:
        """SQLAlchemy + PyMySQL 连接串。"""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    """单例配置，避免重复读取 .env。"""
    return Settings()


settings = get_settings()
