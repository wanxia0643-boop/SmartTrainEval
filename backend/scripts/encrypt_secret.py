"""生成配置密文的小工具。

用法（在 backend 目录下）：
    # 用已有密钥加密
    python -m scripts.encrypt_secret 7454088 --key <CONFIG_ENC_KEY>

    # 不传 key 时自动生成一个新密钥并加密
    python -m scripts.encrypt_secret 7454088

输出：CONFIG_ENC_KEY 与 ENC(...) 密文，分别写入 .env 的
CONFIG_ENC_KEY 和 DB_PASSWORD。密钥务必妥善保管，切勿提交到仓库。
"""
import argparse

from app.utils.crypto import encrypt_secret, generate_key


def main() -> None:
    parser = argparse.ArgumentParser(description="加密配置敏感值")
    parser.add_argument("plaintext", help="待加密的明文，如数据库密码")
    parser.add_argument("--key", default="", help="Fernet 密钥；不传则自动生成")
    args = parser.parse_args()

    key = args.key or generate_key()
    cipher = encrypt_secret(args.plaintext, key)

    print("CONFIG_ENC_KEY=" + key)
    print("DB_PASSWORD=" + cipher)


if __name__ == "__main__":
    main()
