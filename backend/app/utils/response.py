"""
响应工具模块
"""
from typing import Any, Dict, Optional
from fastapi import Response
from fastapi.responses import JSONResponse
import json
import logging

logger = logging.getLogger(__name__)

# 错误码定义
class ErrorCode:
    """错误码常量"""
    SUCCESS = 0
    SYSTEM_ERROR = 10000
    PARAMETER_ERROR = 10001
    AUTHENTICATION_ERROR = 10002
    PERMISSION_ERROR = 10003
    RATE_LIMIT_ERROR = 10004
    DATABASE_ERROR = 10005
    
    # 业务级错误码
    PROJECT_NOT_FOUND = 20001
    PROJECT_NAME_EXISTS = 20002
    INVALID_PROJECT_KEY = 20003
    PERFORMANCE_DATA_INVALID = 20004
    AI_SERVICE_UNAVAILABLE = 20005
    ANALYSIS_IN_PROGRESS = 20006


class ResponseHelper:
    """响应助手类"""
    
    @staticmethod
    def success(data: Any = None, msg: str = "success") -> Dict[str, Any]:
        """成功响应"""
        return {
            "code": ErrorCode.SUCCESS,
            "msg": msg,
            "data": data if data is not None else {}
        }
    
    @staticmethod
    def error(code: int, msg: str, data: Any = None) -> Dict[str, Any]:
        """错误响应"""
        return {
            "code": code,
            "msg": msg,
            "data": data if data is not None else {}
        }
    
    @staticmethod
    def paginated_response(
        items: list,
        total: int,
        page: int,
        size: int,
        msg: str = "success"
    ) -> Dict[str, Any]:
        """分页响应"""
        return {
            "code": ErrorCode.SUCCESS,
            "msg": msg,
            "data": {
                "items": items,
                "pagination": {
                    "total": total,
                    "page": page,
                    "size": size,
                    "pages": (total + size - 1) // size if total > 0 else 0,
                    "has_next": page * size < total,
                    "has_prev": page > 1
                }
            }
        }
    
    @staticmethod
    def json_response(data: Dict[str, Any], status_code: int = 200) -> JSONResponse:
        """JSON响应"""
        return JSONResponse(
            content=data,
            status_code=status_code,
            headers={
                "Content-Type": "application/json; charset=utf-8"
            }
        )


# 便捷函数
def success_response(data: Any = None, msg: str = "success") -> Dict[str, Any]:
    """成功响应便捷函数"""
    return ResponseHelper.success(data, msg)


def error_response(code: int, msg: str, data: Any = None) -> Dict[str, Any]:
    """错误响应便捷函数"""
    return ResponseHelper.error(code, msg, data)


def paginated_response(
    items: list,
    total: int,
    page: int,
    size: int,
    msg: str = "success"
) -> Dict[str, Any]:
    """分页响应便捷函数"""
    return ResponseHelper.paginated_response(items, total, page, size, msg)


# 异常处理器
class APIException(Exception):
    """API异常基类"""
    
    def __init__(self, code: int, msg: str, data: Any = None):
        self.code = code
        self.msg = msg
        self.data = data
        super().__init__(msg)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data if self.data is not None else {}
        }


class ValidationError(APIException):
    """参数验证错误"""
    
    def __init__(self, msg: str, data: Any = None):
        super().__init__(ErrorCode.PARAMETER_ERROR, msg, data)


class NotFoundError(APIException):
    """资源不存在错误"""
    
    def __init__(self, msg: str = "资源不存在", data: Any = None):
        super().__init__(ErrorCode.PROJECT_NOT_FOUND, msg, data)


class BusinessError(APIException):
    """业务逻辑错误"""
    
    def __init__(self, code: int, msg: str, data: Any = None):
        super().__init__(code, msg, data)


class SystemError(APIException):
    """系统错误"""
    
    def __init__(self, msg: str = "系统错误", data: Any = None):
        super().__init__(ErrorCode.SYSTEM_ERROR, msg, data)


# 数据格式化工具
class DataFormatter:
    """数据格式化工具"""
    
    @staticmethod
    def format_datetime(dt) -> Optional[str]:
        """格式化日期时间"""
        if dt is None:
            return None
        try:
            return dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)
        except Exception:
            return None
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化耗时"""
        if seconds < 0.001:
            return f"{seconds * 1000000:.0f}μs"
        elif seconds < 1:
            return f"{seconds * 1000:.1f}ms"
        else:
            return f"{seconds:.3f}s"
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}PB"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 2) -> str:
        """格式化百分比"""
        return f"{value * 100:.{decimal_places}f}%"
    
    @staticmethod
    def clean_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """清理敏感数据"""
        sensitive_keys = {
            'password', 'token', 'secret', 'key', 'authorization',
            'cookie', 'session', 'csrf', 'api_key'
        }
        
        def clean_dict(d):
            if not isinstance(d, dict):
                return d
            
            cleaned = {}
            for k, v in d.items():
                if isinstance(k, str) and any(sensitive in k.lower() for sensitive in sensitive_keys):
                    cleaned[k] = "[FILTERED]"
                elif isinstance(v, dict):
                    cleaned[k] = clean_dict(v)
                elif isinstance(v, list):
                    cleaned[k] = [clean_dict(item) if isinstance(item, dict) else item for item in v]
                else:
                    cleaned[k] = v
            return cleaned
        
        return clean_dict(data)


# 响应装饰器
def format_response(func):
    """格式化响应装饰器"""
    from functools import wraps
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            
            # 如果结果已经是标准格式，直接返回
            if isinstance(result, dict) and "code" in result:
                return result
            
            # 否则包装为成功响应
            return success_response(result)
            
        except APIException as e:
            logger.warning(f"API异常: {e.msg}")
            return e.to_dict()
        except Exception as e:
            logger.error(f"未处理的异常: {str(e)}", exc_info=True)
            return error_response(ErrorCode.SYSTEM_ERROR, "系统错误")
    
    return wrapper


# 性能统计格式化
class PerformanceFormatter:
    """性能数据格式化工具"""
    
    @staticmethod
    def format_performance_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """格式化性能记录"""
        formatter = DataFormatter()
        
        return {
            "trace_id": record.get("trace_id"),
            "project_key": record.get("project_key"),
            "request": {
                "method": record.get("request_info", {}).get("method"),
                "path": record.get("request_info", {}).get("path"),
                "query_params": record.get("request_info", {}).get("query_params", {}),
                "remote_ip": record.get("request_info", {}).get("remote_ip")
            },
            "response": {
                "status_code": record.get("response_info", {}).get("status_code"),
                "size": formatter.format_bytes(record.get("response_info", {}).get("response_size", 0))
            },
            "performance": {
                "total_duration": formatter.format_duration(
                    record.get("performance_metrics", {}).get("total_duration", 0)
                ),
                "cpu_time": formatter.format_duration(
                    record.get("performance_metrics", {}).get("cpu_time", 0)
                ),
                "memory_peak": formatter.format_bytes(
                    record.get("performance_metrics", {}).get("memory_usage", {}).get("peak_memory", 0) * 1024 * 1024
                ),
                "function_count": len(record.get("function_calls", []))
            },
            "timestamp": formatter.format_datetime(record.get("timestamp")),
            "created_at": formatter.format_datetime(record.get("created_at"))
        }
    
    @staticmethod
    def format_analysis_result(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """格式化分析结果"""
        formatter = DataFormatter()
        
        formatted = {
            "analysis_id": analysis.get("analysis_id"),
            "project_key": analysis.get("project_key"),
            "trace_id": analysis.get("trace_id"),
            "status": analysis.get("status"),
            "analysis_type": analysis.get("analysis_type"),
            "created_at": formatter.format_datetime(analysis.get("created_at")),
            "completed_at": formatter.format_datetime(analysis.get("completed_at"))
        }
        
        # 添加分析结果（如果已完成）
        if analysis.get("analysis_results"):
            results = analysis["analysis_results"]
            formatted["results"] = {
                "performance_score": results.get("performance_score"),
                "bottleneck_count": len(results.get("bottleneck_analysis", [])),
                "suggestion_count": len(results.get("optimization_suggestions", [])),
                "risk_count": len(results.get("risk_assessment", {}).get("current_risks", []))
            }
        
        return formatted