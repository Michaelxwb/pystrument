"""
Flask装饰器 - 兼容导入
"""
from ..utils.decorator import monitor_performance

def monitor_function(name=None, tags=None):
    """函数监控装饰器"""
    return monitor_performance(
        custom_tags=tags
    )
