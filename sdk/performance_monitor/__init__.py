"""
性能监控SDK - 主入口模块
"""

__version__ = "1.0.0"
__author__ = "Performance Monitor Team"

from .core.collector import PerformanceCollector
from .core.profiler import ProfilerManager
from .core.sender import DataSender
from .utils.config import Config

# 导入框架集成模块
from .flask import PerformanceMiddleware as FlaskMiddleware
from .django import PerformanceMiddleware as DjangoMiddleware
from .fastapi import PerformanceMiddleware as FastAPIMiddleware

# 便捷导入
from .utils.decorator import monitor_performance

__all__ = [
    "PerformanceCollector",
    "ProfilerManager", 
    "DataSender",
    "Config",
    "FlaskMiddleware",
    "DjangoMiddleware", 
    "FastAPIMiddleware",
    "monitor_performance"
]

# 全局配置实例
_global_config = None

def configure(project_key: str, api_endpoint: str, **kwargs):
    """全局配置SDK"""
    global _global_config
    _global_config = Config(
        project_key=project_key,
        api_endpoint=api_endpoint,
        **kwargs
    )
    return _global_config

def get_config():
    """获取全局配置"""
    return _global_config