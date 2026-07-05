"""魔珐星云数字人运行时配置。"""
from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.deps import require_roles
from app.core.response import success
from app.schemas.auth import CurrentUser
from app.utils.enums import RoleCode

router = APIRouter(prefix="/xingyun", tags=["魔珐星云数字人"])


@router.get("/config", summary="获取魔珐星云数字人 SDK 配置")
def get_xingyun_config(
    _: CurrentUser = Depends(
        require_roles(RoleCode.TEACHER, RoleCode.ENTERPRISE, RoleCode.ADMIN)
    ),
):
    """返回前端初始化 XmovAvatar Lite SDK 需要的运行时配置。

    App Secret 不写入前端源码，只从本地后端环境变量读取。注意：Lite SDK
    初始化时仍需要浏览器拿到该值，这是官方 H5 接入方式的要求。
    """
    enabled = bool(settings.xingyun_app_id and settings.xingyun_app_secret)
    return success(
        data={
            "enabled": enabled,
            "app_id": settings.xingyun_app_id if enabled else "",
            "app_secret": settings.xingyun_app_secret if enabled else "",
            "gateway_server": settings.xingyun_gateway_server,
            "sdk_url": settings.xingyun_sdk_url,
        }
    )
