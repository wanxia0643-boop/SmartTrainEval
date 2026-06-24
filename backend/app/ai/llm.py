"""LangChain 大模型客户端封装入口。

统一在此处构建 LLM 实例，业务模块通过 get_llm() 获取，便于切换厂商/模型。
"""
from functools import lru_cache
from typing import Any

from app.core.config import settings
from app.utils.logger import logger


@lru_cache
def get_llm() -> Any:
    """构建并缓存 LangChain Chat 模型实例。

    默认接入 OpenAI 兼容接口（含国产大模型的 OpenAI 兼容网关）。
    未配置 API Key 时返回 None，调用方需做降级处理。
    """
    if not settings.llm_api_key:
        logger.warning("未配置 LLM_API_KEY，大模型功能不可用")
        return None

    # 延迟导入，避免无 Key 环境强依赖
    from langchain_openai import ChatOpenAI

    kwargs: dict[str, Any] = {
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
        "api_key": settings.llm_api_key,
    }
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url

    logger.info(f"初始化 LLM: provider={settings.llm_provider} model={settings.llm_model}")
    return ChatOpenAI(**kwargs)
