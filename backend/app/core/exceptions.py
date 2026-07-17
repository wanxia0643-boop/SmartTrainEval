"""自定义异常与全局异常处理。"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.response import error
from app.utils.logger import logger


class BusinessException(Exception):
    """业务异常：用于在 service 层抛出可控的业务错误。"""

    def __init__(self, msg: str, code: int = 1, http_status: int | None = None):
        self.msg = msg
        self.code = code
        if http_status is None:
            http_status = code if status.HTTP_400_BAD_REQUEST <= code <= 599 else status.HTTP_200_OK
        self.http_status = http_status
        super().__init__(msg)


class AuthException(BusinessException):
    """认证/授权异常。"""

    def __init__(self, msg: str = "未认证或令牌无效", code: int = 401):
        super().__init__(msg=msg, code=code, http_status=status.HTTP_401_UNAUTHORIZED)


class PermissionException(BusinessException):
    """权限不足异常。"""

    def __init__(self, msg: str = "无权限访问该资源", code: int = 403):
        super().__init__(msg=msg, code=code, http_status=status.HTTP_403_FORBIDDEN)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器，保证所有错误也返回统一结构。"""

    @app.exception_handler(BusinessException)
    async def _business_handler(_: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.http_status,
            content=error(msg=exc.msg, code=exc.code),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(_: Request, exc: RequestValidationError):
        # 提取首条校验错误，简洁返回
        first = exc.errors()[0] if exc.errors() else {}
        loc = ".".join(str(x) for x in first.get("loc", []))
        msg = f"参数校验失败: {loc} {first.get('msg', '')}".strip()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error(msg=msg, code=422),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(_: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error(msg=str(exc.detail), code=exc.status_code),
        )

    @app.exception_handler(Exception)
    async def _global_handler(_: Request, exc: Exception):
        logger.exception(f"未捕获异常: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error(msg="服务器内部错误", code=500),
        )
