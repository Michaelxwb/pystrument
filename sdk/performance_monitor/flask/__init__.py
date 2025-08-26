"""FlaskおAB集成模块"""

from .middleware import PerformanceMiddleware, PerformanceWSGIWrapper
from .decorators import monitor_performance, monitor_function

# 导出中间件类，保持向后兼容
FlaskMiddleware = PerformanceMiddleware

__all__ = [
    "PerformanceMiddleware",
    "FlaskMiddleware",  # 别名
    "PerformanceWSGIWrapper", 
    "monitor_performance",
    "monitor_function"
]