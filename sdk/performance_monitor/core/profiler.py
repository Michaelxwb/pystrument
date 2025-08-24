"""
性能分析器管理模块
"""
import threading
import time
import random
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
import logging

from .collector import PerformanceCollector
from .sender import DataSender
from ..utils.config import Config

logger = logging.getLogger(__name__)


class ProfilerManager:
    """性能分析器管理器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.data_sender = DataSender(config)
        self._local = threading.local()
        self._enabled = config.enabled
        
    @property
    def collector(self) -> Optional[PerformanceCollector]:
        """获取当前线程的收集器"""
        return getattr(self._local, 'collector', None)
    
    @collector.setter
    def collector(self, value: Optional[PerformanceCollector]):
        """设置当前线程的收集器"""
        self._local.collector = value
    
    def should_profile(self, request_context: Dict[str, Any]) -> bool:
        """判断是否应该进行性能分析"""
        if not self._enabled:
            return False
        
        # 检查采样率
        if random.random() > self.config.sampling_rate:
            return False
        
        # 检查排除路径
        path = request_context.get("path", "")
        if self._is_excluded_path(path):
            return False
        
        # 检查包含模式
        if self.config.include_patterns and not self._matches_include_patterns(path):
            return False
        
        return True
    
    def start_profiling(self, request_context: Dict[str, Any]) -> Optional[str]:
        """开始性能分析"""
        try:
            if not self.should_profile(request_context):
                return None
            
            # 创建收集器
            collector = PerformanceCollector(self.config.to_dict())
            trace_id = collector.start_profiling(request_context)
            
            # 保存到线程本地存储
            self.collector = collector
            
            return trace_id
            
        except Exception as e:
            logger.error(f"启动性能分析失败: {str(e)}")
            return None
    
    def stop_profiling(self, response_context: Dict[str, Any]) -> bool:
        """停止性能分析"""
        try:
            collector = self.collector
            if not collector:
                return False
            
            # 收集性能数据
            performance_data = collector.stop_profiling(response_context)
            if not performance_data:
                return False
            
            # 异步发送数据
            if self.config.async_send:
                self.data_sender.send_async(performance_data)
            else:
                self.data_sender.send_sync(performance_data)
            
            return True
            
        except Exception as e:
            logger.error(f"停止性能分析失败: {str(e)}")
            return False
        finally:
            # 清理线程本地存储
            self.collector = None
    
    @contextmanager
    def profile_context(self, request_context: Dict[str, Any], response_context: Dict[str, Any]):
        """性能分析上下文管理器"""
        trace_id = None
        try:
            trace_id = self.start_profiling(request_context)
            yield trace_id
        finally:
            if trace_id:
                self.stop_profiling(response_context)
    
    def _is_excluded_path(self, path: str) -> bool:
        """检查路径是否被排除"""
        for pattern in self.config.exclude_patterns:
            if self._match_pattern(path, pattern):
                return True
        return False
    
    def _matches_include_patterns(self, path: str) -> bool:
        """检查路径是否匹配包含模式"""
        if not self.config.include_patterns:
            return True
        
        for pattern in self.config.include_patterns:
            if self._match_pattern(path, pattern):
                return True
        return False
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """模式匹配"""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def enable(self):
        """启用性能分析"""
        self._enabled = True
        logger.info("性能分析已启用")
    
    def disable(self):
        """禁用性能分析"""
        self._enabled = False
        logger.info("性能分析已禁用")
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        logger.info(f"配置已更新: {kwargs}")


# 全局分析器管理器实例
_profiler_manager: Optional[ProfilerManager] = None


def get_profiler_manager() -> Optional[ProfilerManager]:
    """获取全局分析器管理器"""
    return _profiler_manager


def init_profiler_manager(config: Config) -> ProfilerManager:
    """初始化全局分析器管理器"""
    global _profiler_manager
    _profiler_manager = ProfilerManager(config)
    return _profiler_manager