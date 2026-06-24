"""配置密文工具：对敏感配置（如数据库密码）做对称加解密。

约定采用 jasypt 风格的 ``ENC(<密文>)`` 包裹语法：
  - 配置值形如 ``ENC(gAAAAAB...)`` 时，运行期用密钥解密为明文；
  - 普通明文则原样返回，兼容未加密场景。

加解密基于 cryptography 的 Fernet（AES-128-CBC + HMAC），密钥由
``CONFIG_ENC_KEY`` 提供，仅存放于本地 .env / 环境变量，不入库、不提交。
"""
import re

from cryptography.fernet import Fernet

_ENC_PATTERN = re.compile(r"^ENC\((?P<cipher>.*)\)$", re.S)


def generate_key() -> str:
    """生成一个新的 Fernet 密钥（url-safe base64）。"""
    return Fernet.generate_key().decode()


def is_encrypted(value: str | None) -> bool:
    """判断配置值是否为 ENC(...) 密文。"""
    return bool(value) and _ENC_PATTERN.match(value) is not None


def encrypt_secret(plaintext: str, key: str) -> str:
    """将明文加密为 ``ENC(<密文>)`` 形式。"""
    if not key:
        raise ValueError("缺少加密密钥 CONFIG_ENC_KEY")
    token = Fernet(key.encode()).encrypt(plaintext.encode()).decode()
    return f"ENC({token})"


def decrypt_secret(value: str | None, key: str) -> str:
    """解密 ``ENC(...)`` 密文；若非密文则原样返回。"""
    if not value:
        return value or ""
    match = _ENC_PATTERN.match(value)
    if not match:
        return value  # 明文，直接返回（兼容未加密）
    if not key:
        raise ValueError("检测到加密配置，但缺少解密密钥 CONFIG_ENC_KEY")
    return Fernet(key.encode()).decrypt(match.group("cipher").encode()).decode()
