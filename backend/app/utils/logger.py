"""日志配置：基于 loguru，输出到控制台与文件。"""
import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    ),
)
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    level="INFO",
    rotation="00:00",       # 每天 0 点切分
    retention="30 days",    # 保留 30 天
    encoding="utf-8",
    enqueue=True,           # 多进程/异步安全
)

__all__ = ["logger"]
