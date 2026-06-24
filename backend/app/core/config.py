"""全局配置：从环境变量 / .env 读取并集中管理。"""
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils.crypto import decrypt_secret


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
    db_password: str = ""  # 支持 ENC(...) 密文，运行期用 config_enc_key 解密
    db_name: str = "smart_train_eval"
    db_echo: bool = False

    # 配置加密密钥（仅存于本地 .env / 环境变量，切勿提交）
    config_enc_key: str = ""

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
        """SQLAlchemy + PyMySQL 连接串。

        db_password 支持 ``ENC(...)`` 密文，运行期自动解密；
        密码做 URL 编码，兼容含特殊字符的密码。
        """
        password = decrypt_secret(self.db_password, self.config_enc_key)
        return (
            f"mysql+pymysql://{quote_plus(self.db_user)}:{quote_plus(password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    """单例配置，避免重复读取 .env。"""
    return Settings()


settings = get_settings()
