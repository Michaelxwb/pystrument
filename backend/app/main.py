"""
基于Pyinstrument的性能分析平台 - 后端主应用
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.config.settings import settings
from app.middleware.cors import setup_cors
from app.middleware.response import setup_response_middleware
from app.api.v1 import projects, performance, analysis, dashboard, settings as settings_api, test_analysis, test_analysis_fix
from app.utils.database import init_database, close_database


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在启动性能分析平台后端服务...")
    await init_database()
    logger.info("数据库初始化完成")
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭后端服务...")
    await close_database()
    logger.info("数据库连接已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="性能分析平台API",
    description="基于Pyinstrument的性能分析和监控平台",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# 设置CORS
setup_cors(app)

# 设置统一响应中间件
setup_response_middleware(app)

# 注册API路由
app.include_router(projects.router, prefix="/api/v1/projects", tags=["项目管理"])
app.include_router(performance.router, prefix="/api/v1/performance", tags=["性能数据"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["AI分析"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["仪表盘"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["系统设置"])
app.include_router(test_analysis.router, prefix="/api/v1/test-analysis", tags=["测试分析"])
app.include_router(test_analysis_fix.router, prefix="/api/v1/test-analysis-fix", tags=["修复分析"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "service": "性能分析平台API",
            "version": "1.0.0",
            "status": "running"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "status": "healthy",
            "service": "performance-monitor-api"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 10000,
            "msg": "系统错误",
            "data": {}
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )