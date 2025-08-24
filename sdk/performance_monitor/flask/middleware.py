"""
Flask应用性能监控中间件
"""
import time
from typing import Dict, Any, Optional
from flask import Flask, request, g
from werkzeug.wrappers import Response
import logging

from ..core.profiler import ProfilerManager, init_profiler_manager
from ..utils.config import Config

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    """Flask性能监控中间件"""
    
    def __init__(self, app: Flask, config: Optional[Dict[str, Any]] = None, **kwargs):
        self.app = app
        
        # 初始化配置
        if isinstance(config, dict):
            self.config = Config.from_dict(config)
        elif isinstance(config, Config):
            self.config = config
        else:
            # 从环境变量或参数创建配置
            config_dict = kwargs
            if 'project_key' not in config_dict:
                raise ValueError("project_key是必需的参数")
            if 'api_endpoint' not in config_dict:
                raise ValueError("api_endpoint是必需的参数")
            
            self.config = Config.from_dict(config_dict)
        
        # 验证配置
        self.config.validate()
        
        # 初始化性能分析器
        self.profiler_manager = init_profiler_manager(self.config)
        
        # 注册Flask钩子
        self._register_hooks()
        
        logger.info(f"Flask性能监控中间件已初始化: {self.config}")
    
    def _register_hooks(self):
        """注册Flask请求钩子"""
        
        @self.app.before_request
        def before_request():
            """请求开始前的处理"""
            try:
                # 构建请求上下文
                request_context = self._build_request_context()
                
                # 开始性能分析
                trace_id = self.profiler_manager.start_profiling(request_context)
                if trace_id:
                    g.performance_trace_id = trace_id
                    g.performance_start_time = time.time()
                    
            except Exception as e:
                logger.error(f"Flask before_request 处理失败: {str(e)}")
        
        @self.app.after_request
        def after_request(response: Response):
            """请求结束后的处理"""
            try:
                # 检查是否启动了性能分析
                if hasattr(g, 'performance_trace_id'):
                    # 构建响应上下文
                    response_context = self._build_response_context(response)
                    
                    # 停止性能分析
                    self.profiler_manager.stop_profiling(response_context)
                    
            except Exception as e:
                logger.error(f"Flask after_request 处理失败: {str(e)}")
            
            return response
        
        @self.app.teardown_request
        def teardown_request(exception):
            """请求清理"""
            try:
                # 清理线程本地变量
                if hasattr(g, 'performance_trace_id'):
                    delattr(g, 'performance_trace_id')
                if hasattr(g, 'performance_start_time'):
                    delattr(g, 'performance_start_time')
                    
            except Exception as e:
                logger.error(f"Flask teardown_request 处理失败: {str(e)}")
    
    def _build_request_context(self) -> Dict[str, Any]:
        """构建请求上下文"""
        try:
            return {
                "method": request.method,
                "path": request.path,
                "query_params": dict(request.args),
                "headers": dict(request.headers),
                "remote_ip": request.remote_addr,
                "content_length": request.content_length or 0,
                "content_type": request.content_type
            }
        except Exception as e:
            logger.error(f"构建请求上下文失败: {str(e)}")
            return {}
    
    def _build_response_context(self, response: Response) -> Dict[str, Any]:
        """构建响应上下文"""
        try:
            return {
                "status_code": response.status_code,
                "response_size": len(response.get_data()) if response.get_data() else 0,
                "content_type": response.content_type,
                "headers": dict(response.headers)
            }
        except Exception as e:
            logger.error(f"构建响应上下文失败: {str(e)}")
            return {}


class PerformanceWSGIWrapper:
    """Flask WSGI包装器（另一种集成方式）"""
    
    def __init__(self, flask_app: Flask, project_key: str, api_endpoint: str, **kwargs):
        self.flask_app = flask_app
        
        # 创建配置
        config_dict = {
            "project_key": project_key,
            "api_endpoint": api_endpoint,
            **kwargs
        }
        self.config = Config.from_dict(config_dict)
        self.config.validate()
        
        # 初始化性能分析器
        self.profiler_manager = init_profiler_manager(self.config)
        
        logger.info(f"Flask WSGI包装器已初始化: {self.config}")
    
    def __call__(self, environ, start_response):
        """WSGI应用调用"""
        def new_start_response(status, response_headers, exc_info=None):
            # 在这里可以捕获响应信息
            return start_response(status, response_headers, exc_info)
        
        # 构建请求上下文
        request_context = self._build_request_context_from_environ(environ)
        
        # 开始性能分析
        trace_id = self.profiler_manager.start_profiling(request_context)
        
        try:
            # 调用原始Flask应用
            app_iter = self.flask_app(environ, new_start_response)
            
            # 收集响应数据
            response_data = b''.join(app_iter)
            
            if trace_id:
                # 构建响应上下文
                response_context = {
                    "status_code": 200,  # 从start_response中获取
                    "response_size": len(response_data),
                    "content_type": "application/json"  # 默认值
                }
                
                # 停止性能分析
                self.profiler_manager.stop_profiling(response_context)
            
            return [response_data]
            
        except Exception as e:
            logger.error(f"WSGI包装器执行失败: {str(e)}")
            if trace_id:
                # 记录错误响应
                response_context = {
                    "status_code": 500,
                    "response_size": 0,
                    "content_type": "text/plain"
                }
                self.profiler_manager.stop_profiling(response_context)
            raise
    
    def _build_request_context_from_environ(self, environ: Dict[str, Any]) -> Dict[str, Any]:
        """从WSGI environ构建请求上下文"""
        try:
            return {
                "method": environ.get("REQUEST_METHOD", "GET"),
                "path": environ.get("PATH_INFO", "/"),
                "query_params": self._parse_query_string(environ.get("QUERY_STRING", "")),
                "headers": self._extract_headers_from_environ(environ),
                "remote_ip": environ.get("REMOTE_ADDR"),
                "content_length": int(environ.get("CONTENT_LENGTH", 0) or 0),
                "content_type": environ.get("CONTENT_TYPE")
            }
        except Exception as e:
            logger.error(f"从environ构建请求上下文失败: {str(e)}")
            return {}
    
    def _parse_query_string(self, query_string: str) -> Dict[str, str]:
        """解析查询字符串"""
        try:
            from urllib.parse import parse_qs
            parsed = parse_qs(query_string)
            return {k: v[0] if v else '' for k, v in parsed.items()}
        except Exception:
            return {}
    
    def _extract_headers_from_environ(self, environ: Dict[str, Any]) -> Dict[str, str]:
        """从environ提取HTTP头"""
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        return headers
    
    def run(self, host='127.0.0.1', port=5000, debug=None, **options):
        """运行Flask应用（保持与Flask.run相同的接口）"""
        return self.flask_app.run(host=host, port=port, debug=debug, **options)
    
    def __getattr__(self, name):
        """代理Flask应用的其他属性"""
        return getattr(self.flask_app, name)