"""路由层：聚合所有业务路由。"""
from fastapi import APIRouter

from app.routers import (
    achievement,
    ai,
    auth,
    eval_result,
    indicator,
    llm_log,
    org,
    project,
    report,
    role,
    upload,
    user,
    xingyun,
)

# 汇总路由，统一挂载到 main 中（带 API 前缀）
api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(role.router)
api_router.include_router(org.router)
api_router.include_router(project.router)
api_router.include_router(achievement.router)
api_router.include_router(indicator.router)
api_router.include_router(eval_result.router)
api_router.include_router(llm_log.router)
api_router.include_router(report.router)
api_router.include_router(ai.router)
api_router.include_router(upload.router)
api_router.include_router(xingyun.router)

__all__ = ["api_router"]
