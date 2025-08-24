"""
Flask装饰器支持
"""
import functools
from typing import Dict, Any, Optional, Callable
from flask import request, g
import logging

from ..core.profiler import get_profiler_manager
from ..utils.config import Config

logger = logging.getLogger(__name__)


def monitor_performance(
    track_sql: bool = True,
    track_memory: bool = True,
    custom_tags: Optional[Dict[str, Any]] = None,
    enabled: Optional[bool] = None
):
    """
    Flask视图函数性能监控装饰器
    
    Args:
        track_sql: 是否跟踪SQL查询
        track_memory: 是否跟踪内存使用
        custom_tags: 自定义标签
        enabled: 是否启用监控（None表示使用全局配置）
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler_manager = get_profiler_manager()
            
            # 检查是否启用监控
            if enabled is False or (enabled is None and profiler_manager and not profiler_manager._enabled):
                return func(*args, **kwargs)
            
            if not profiler_manager:
                logger.warning("性能分析器未初始化，跳过监控")
                return func(*args, **kwargs)
            
            # 构建请求上下文
            request_context = _build_request_context_for_decorator(func, custom_tags)
            
            # 开始性能分析
            trace_id = profiler_manager.start_profiling(request_context)
            
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 构建响应上下文
                response_context = _build_response_context_for_decorator(result)
                
                return result
                
            except Exception as e:
                # 记录异常响应
                response_context = {
                    "status_code": 500,
                    "response_size": 0,
                    "content_type": "application/json",
                    "error": str(e)
                }
                raise
            finally:
                if trace_id:
                    profiler_manager.stop_profiling(response_context)
        
        return wrapper
    return decorator


def _build_request_context_for_decorator(func: Callable, custom_tags: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """为装饰器构建请求上下文"""
    try:
        context = {
            "method": getattr(request, 'method', 'UNKNOWN'),
            "path": getattr(request, 'path', f'/{func.__name__}'),
            "query_params": dict(getattr(request, 'args', {})),
            "headers": dict(getattr(request, 'headers', {})),
            "remote_ip": getattr(request, 'remote_addr', None),
            "function_name": func.__name__,
            "module_name": func.__module__,
        }
        
        # 添加自定义标签
        if custom_tags:
            context["custom_tags"] = custom_tags
        
        return context
        
    except Exception as e:
        logger.error(f"构建装饰器请求上下文失败: {str(e)}")
        return {
            "method": "UNKNOWN",
            "path": f"/{func.__name__}",
            "function_name": func.__name__,
            "module_name": func.__module__,
        }


def _build_response_context_for_decorator(result: Any) -> Dict[str, Any]:
    """为装饰器构建响应上下文"""
    try:
        if hasattr(result, 'status_code'):
            # Flask Response对象
            return {
                "status_code": result.status_code,
                "response_size": len(result.get_data()) if hasattr(result, 'get_data') else 0,
                "content_type": getattr(result, 'content_type', 'application/json')
            }
        else:
            # 普通返回值
            import json
            response_size = 0
            try:
                if isinstance(result, (dict, list)):
                    response_size = len(json.dumps(result, ensure_ascii=False))
                elif isinstance(result, str):
                    response_size = len(result.encode('utf-8'))
            except:
                pass
            
            return {
                "status_code": 200,
                "response_size": response_size,
                "content_type": "application/json"
            }
            
    except Exception as e:
        logger.error(f"构建装饰器响应上下文失败: {str(e)}")
        return {
            "status_code": 200,
            "response_size": 0,
            "content_type": "application/json"
        }


def monitor_function(
    name: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None
):
    """
    通用函数性能监控装饰器
    
    Args:
        name: 自定义函数名称
        tags: 自定义标签
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler_manager = get_profiler_manager()
            
            if not profiler_manager or not profiler_manager._enabled:
                return func(*args, **kwargs)
            
            # 使用函数级别的临时性能分析
            function_name = name or func.__name__
            
            # 记录函数开始时间
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # 记录函数执行时间
                duration = time.time() - start_time
                logger.debug(f"函数 {function_name} 执行耗时: {duration:.3f}s")
                
                # 如果有活跃的trace，添加函数信息
                if hasattr(g, 'performance_trace_id'):
                    # TODO: 将函数信息添加到当前trace中
                    pass
        
        return wrapper
    return decorator