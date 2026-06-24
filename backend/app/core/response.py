"""统一响应格式：{ code, msg, data }。"""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一返回结构，供 OpenAPI 文档展示。"""

    code: int = 0
    msg: str = "success"
    data: T | None = None


def success(data: Any = None, msg: str = "success", code: int = 0) -> dict[str, Any]:
    """成功响应。code=0 约定为成功。"""
    return {"code": code, "msg": msg, "data": data}


def error(msg: str = "error", code: int = 1, data: Any = None) -> dict[str, Any]:
    """失败响应。"""
    return {"code": code, "msg": msg, "data": data}
