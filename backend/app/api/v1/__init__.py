"""
API v1 路由模块初始化
"""

# 导入所有路由模块，确保FastAPI能够正确注册路由
from . import projects, performance, analysis

__all__ = ["projects", "performance", "analysis"]