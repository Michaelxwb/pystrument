"""
统一响应体封装中间件
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json
import time
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


class ResponseMiddleware(BaseHTTPMiddleware):
    """统一响应体中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求和响应"""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # 记录请求日志
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # 处理未捕获的异常
            logger.error(f"请求处理异常: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "code": ErrorCode.SYSTEM_ERROR,
                    "msg": "系统错误",
                    "data": {}
                }
            )


def setup_response_middleware(app: FastAPI):
    """设置响应中间件"""
    app.add_middleware(ResponseMiddleware)


def success_response(data=None, msg="success"):
    """成功响应"""
    return {
        "code": ErrorCode.SUCCESS,
        "msg": msg,
        "data": data if data is not None else {}
    }


def error_response(code: int, msg: str, data=None):
    """错误响应"""
    return {
        "code": code,
        "msg": msg,
        "data": data if data is not None else {}
    }