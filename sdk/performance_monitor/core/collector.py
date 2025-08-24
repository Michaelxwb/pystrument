"""
性能数据收集器核心模块
"""
import time
import uuid
import psutil
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from pyinstrument import Profiler
import logging

logger = logging.getLogger(__name__)


class PerformanceCollector:
    """性能数据收集器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.profiler: Optional[Profiler] = None
        self.start_time: Optional[float] = None
        self.trace_id: Optional[str] = None
        self.request_info: Dict[str, Any] = {}
        self.start_memory: int = 0
        
    def start_profiling(self, request_context: Dict[str, Any]) -> str:
        """开始性能分析"""
        try:
            # 生成唯一的trace_id
            self.trace_id = f"trace_{uuid.uuid4().hex[:16]}"
            self.start_time = time.time()
            
            # 记录开始时的内存使用
            process = psutil.Process()
            self.start_memory = process.memory_info().rss // 1024 // 1024  # MB
            
            # 创建并启动profiler
            self.profiler = Profiler(interval=0.001, async_mode='disabled')
            self.profiler.start()
            
            # 保存请求上下文
            self.request_info = self._extract_request_info(request_context)
            
            logger.debug(f"开始性能分析: {self.trace_id}")
            return self.trace_id
            
        except Exception as e:
            logger.error(f"启动性能分析失败: {str(e)}")
            raise
    
    def stop_profiling(self, response_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """停止性能分析并收集数据"""
        try:
            if not self.profiler or not self.start_time:
                logger.warning("性能分析器未启动")
                return None
            
            # 停止profiler
            self.profiler.stop()
            
            # 计算总耗时
            total_duration = time.time() - self.start_time
            
            # 计算内存使用
            process = psutil.Process()
            end_memory = process.memory_info().rss // 1024 // 1024  # MB
            memory_delta = end_memory - self.start_memory
            
            # 提取响应信息
            response_info = self._extract_response_info(response_context)
            
            # 解析函数调用栈
            function_calls = self._parse_function_calls()
            
            # 构建性能记录
            performance_record = {
                "trace_id": self.trace_id,
                "request_info": self.request_info,
                "response_info": response_info,
                "performance_metrics": {
                    "total_duration": total_duration,
                    "cpu_time": self.profiler.cpu_time,
                    "memory_usage": {
                        "peak_memory": end_memory,
                        "memory_delta": memory_delta
                    },
                    "database_metrics": {
                        "query_count": 0,  # TODO: 从profiler中提取SQL查询信息
                        "query_time": 0.0,
                        "slow_queries": 0
                    },
                    "cache_metrics": {
                        "cache_hits": 0,
                        "cache_misses": 0,
                        "cache_time": 0.0
                    }
                },
                "function_calls": function_calls,
                "version_info": self._get_version_info(),
                "environment": self._get_environment_info()
            }
            
            logger.debug(f"性能分析完成: {self.trace_id}, 耗时: {total_duration:.3f}s")
            return performance_record
            
        except Exception as e:
            logger.error(f"停止性能分析失败: {str(e)}")
            return None
        finally:
            # 清理状态
            self._reset_state()
    
    def _extract_request_info(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """提取请求信息"""
        try:
            return {
                "method": request_context.get("method", "GET"),
                "path": request_context.get("path", "/"),
                "query_params": request_context.get("query_params", {}),
                "headers": self._filter_headers(request_context.get("headers", {})),
                "user_agent": request_context.get("headers", {}).get("User-Agent"),
                "remote_ip": request_context.get("remote_ip")
            }
        except Exception as e:
            logger.error(f"提取请求信息失败: {str(e)}")
            return {}
    
    def _extract_response_info(self, response_context: Dict[str, Any]) -> Dict[str, Any]:
        """提取响应信息"""
        try:
            return {
                "status_code": response_context.get("status_code", 200),
                "response_size": response_context.get("response_size", 0),
                "content_type": response_context.get("content_type", "application/json")
            }
        except Exception as e:
            logger.error(f"提取响应信息失败: {str(e)}")
            return {}
    
    def _parse_function_calls(self) -> List[Dict[str, Any]]:
        """解析函数调用栈"""
        try:
            if not self.profiler.last_session:
                return []
            
            function_calls = []
            call_order = 0
            
            def traverse_frame(frame, parent_id=None, depth=0):
                nonlocal call_order
                
                # 过滤掉系统和库函数
                if self._should_skip_frame(frame):
                    for child in frame.children:
                        traverse_frame(child, parent_id, depth)
                    return
                
                call_id = f"{self.trace_id}_call_{call_order}"
                call_order += 1
                
                function_call = {
                    "call_id": call_id,
                    "parent_call_id": parent_id,
                    "function_name": frame.function,
                    "file_path": frame.file_path,
                    "line_number": frame.line_no,
                    "duration": frame.time,
                    "depth": depth,
                    "call_order": call_order
                }
                
                function_calls.append(function_call)
                
                # 递归处理子函数
                for child in frame.children:
                    traverse_frame(child, call_id, depth + 1)
            
            # 遍历调用栈
            root_frame = self.profiler.last_session.root_frame()
            if root_frame:
                for child in root_frame.children:
                    traverse_frame(child, None, 0)
            
            return function_calls
            
        except Exception as e:
            logger.error(f"解析函数调用栈失败: {str(e)}")
            return []
    
    def _should_skip_frame(self, frame) -> bool:
        """判断是否应该跳过某个调用帧"""
        # 跳过系统库和第三方库
        skip_patterns = [
            '/usr/lib/',
            '/usr/local/lib/',
            'site-packages/',
            '<built-in>',
            '<frozen',
            'performance_monitor/',  # 跳过自身
        ]
        
        file_path = getattr(frame, 'file_path', '')
        if not file_path:
            return True
            
        for pattern in skip_patterns:
            if pattern in file_path:
                return True
        
        # 跳过耗时太短的函数（小于1ms）
        if getattr(frame, 'time', 0) < 0.001:
            return True
        
        return False
    
    def _filter_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """过滤敏感的请求头"""
        sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token',
            'x-csrf-token', 'x-access-token'
        }
        
        filtered = {}
        for key, value in headers.items():
            if key.lower() not in sensitive_headers:
                filtered[key] = value
            else:
                filtered[key] = "[FILTERED]"
        
        return filtered
    
    def _get_version_info(self) -> Dict[str, Any]:
        """获取版本信息"""
        try:
            return {
                "app_version": self.config.get("app_version"),
                "git_commit": self.config.get("git_commit"),
                "deploy_time": self.config.get("deploy_time")
            }
        except Exception:
            return {}
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        try:
            import sys
            import platform
            
            return {
                "python_version": sys.version.split()[0],
                "framework_version": self.config.get("framework_version"),
                "server_info": f"{platform.system()} {platform.release()}"
            }
        except Exception:
            return {}
    
    def _reset_state(self):
        """重置状态"""
        self.profiler = None
        self.start_time = None
        self.trace_id = None
        self.request_info = {}
        self.start_memory = 0