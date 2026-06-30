"""FastAPI 应用入口。"""
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# 确保 backend 目录在 sys.path 中，支持在 PyCharm 直接右键运行本文件
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.response import success
from app.routers import api_router
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期：启动/关闭钩子。"""
    logger.info(f"{settings.app_name} 启动中 env={settings.app_env}")
    yield
    logger.info(f"{settings.app_name} 已关闭")


def create_app() -> FastAPI:
    """应用工厂。"""
    app = FastAPI(
        title=settings.app_name,
        description="软件实训评价系统 后端 API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    # CORS（开发期放开，生产请收敛 allow_origins）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 全局异常处理
    register_exception_handlers(app)

    # 路由
    app.include_router(api_router, prefix=settings.api_prefix)
    (_BACKEND_DIR / "uploads").mkdir(exist_ok=True)
    (_BACKEND_DIR / "generated").mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(_BACKEND_DIR / "uploads")), name="uploads")
    app.mount("/generated", StaticFiles(directory=str(_BACKEND_DIR / "generated")), name="generated")

    @app.get("/health", tags=["系统"], summary="健康检查")
    def health():
        return success(data={"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    # 便于在 PyCharm 中直接右键运行本文件启动（工作目录需为 backend）
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
