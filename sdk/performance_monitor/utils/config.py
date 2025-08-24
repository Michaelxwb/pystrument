"""
SDK配置管理模块
"""
import os
import yaml
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """SDK配置类"""
    
    # 必需配置
    project_key: str
    api_endpoint: str
    
    # 基础配置
    enabled: bool = True
    sampling_rate: float = 0.3
    async_send: bool = True
    
    # 过滤配置
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "/health", "/metrics", "/static/*", "*.css", "*.js", "*.ico"
    ])
    include_patterns: List[str] = field(default_factory=list)
    
    # 数据传输配置
    batch_size: int = 50
    batch_timeout: float = 5.0
    request_timeout: int = 10
    retry_times: int = 3
    retry_delay: float = 1.0
    
    # 监控配置
    track_sql: bool = True
    track_cache: bool = True
    track_memory: bool = True
    track_templates: bool = False
    
    # 安全配置
    max_request_size: int = 10485760  # 10MB
    max_response_size: int = 10485760  # 10MB
    
    # 版本信息
    sdk_version: str = "1.0.0"
    app_version: Optional[str] = None
    git_commit: Optional[str] = None
    deploy_time: Optional[str] = None
    framework_version: Optional[str] = None
    
    # 日志配置
    log_level: str = "INFO"
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """从字典创建配置"""
        # 过滤掉不存在的字段
        valid_fields = {f.name for f in cls.__dataclasses_fields__.values()}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        
        return cls(**filtered_dict)
    
    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """从配置文件创建配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:  # JSON
                    config_data = json.load(f)
            
            # 处理嵌套的performance_monitor配置
            if 'performance_monitor' in config_data:
                config_data = config_data['performance_monitor']
            
            return cls.from_dict(config_data)
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            raise
    
    @classmethod
    def from_env(cls, prefix: str = "PERFORMANCE_MONITOR_") -> "Config":
        """从环境变量创建配置"""
        config_dict = {}
        
        # 必需配置
        project_key = os.getenv(f"{prefix}PROJECT_KEY")
        api_endpoint = os.getenv(f"{prefix}API_ENDPOINT")
        
        if not project_key or not api_endpoint:
            raise ValueError("项目密钥和API端点是必需的配置")
        
        config_dict.update({
            "project_key": project_key,
            "api_endpoint": api_endpoint
        })
        
        # 可选配置
        env_mappings = {
            "enabled": (f"{prefix}ENABLED", bool),
            "sampling_rate": (f"{prefix}SAMPLING_RATE", float),
            "async_send": (f"{prefix}ASYNC_SEND", bool),
            "batch_size": (f"{prefix}BATCH_SIZE", int),
            "batch_timeout": (f"{prefix}BATCH_TIMEOUT", float),
            "request_timeout": (f"{prefix}REQUEST_TIMEOUT", int),
            "retry_times": (f"{prefix}RETRY_TIMES", int),
            "retry_delay": (f"{prefix}RETRY_DELAY", float),
            "track_sql": (f"{prefix}TRACK_SQL", bool),
            "track_cache": (f"{prefix}TRACK_CACHE", bool),
            "track_memory": (f"{prefix}TRACK_MEMORY", bool),
            "track_templates": (f"{prefix}TRACK_TEMPLATES", bool),
            "app_version": (f"{prefix}APP_VERSION", str),
            "git_commit": (f"{prefix}GIT_COMMIT", str),
            "deploy_time": (f"{prefix}DEPLOY_TIME", str),
            "log_level": (f"{prefix}LOG_LEVEL", str),
        }
        
        for key, (env_key, data_type) in env_mappings.items():
            value = os.getenv(env_key)
            if value is not None:
                try:
                    if data_type == bool:
                        config_dict[key] = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        config_dict[key] = data_type(value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"环境变量 {env_key} 转换失败: {str(e)}")
        
        # 处理列表类型的环境变量
        exclude_patterns = os.getenv(f"{prefix}EXCLUDE_PATTERNS")
        if exclude_patterns:
            config_dict["exclude_patterns"] = [p.strip() for p in exclude_patterns.split(',')]
        
        include_patterns = os.getenv(f"{prefix}INCLUDE_PATTERNS")
        if include_patterns:
            config_dict["include_patterns"] = [p.strip() for p in include_patterns.split(',')]
        
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for field_info in self.__dataclass_fields__.values():
            value = getattr(self, field_info.name)
            result[field_info.name] = value
        return result
    
    def validate(self) -> bool:
        """验证配置"""
        try:
            # 检查必需字段
            if not self.project_key:
                raise ValueError("项目密钥不能为空")
            
            if not self.api_endpoint:
                raise ValueError("API端点不能为空")
            
            # 检查数值范围
            if not 0 <= self.sampling_rate <= 1:
                raise ValueError("采样率必须在0-1之间")
            
            if self.batch_size <= 0:
                raise ValueError("批量大小必须大于0")
            
            if self.batch_timeout <= 0:
                raise ValueError("批量超时时间必须大于0")
            
            if self.request_timeout <= 0:
                raise ValueError("请求超时时间必须大于0")
            
            if self.retry_times < 0:
                raise ValueError("重试次数不能为负数")
            
            return True
            
        except Exception as e:
            logger.error(f"配置验证失败: {str(e)}")
            raise
    
    def update(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"未知配置项: {key}")
    
    def save_to_file(self, config_path: str):
        """保存配置到文件"""
        try:
            config_data = self.to_dict()
            
            with open(config_path, 'w', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    yaml.dump({"performance_monitor": config_data}, f, default_flow_style=False)
                else:  # JSON
                    json.dump({"performance_monitor": config_data}, f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存到: {config_path}")
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            raise
    
    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"Config(project_key={self.project_key[:8]}..., "
            f"api_endpoint={self.api_endpoint}, "
            f"enabled={self.enabled}, "
            f"sampling_rate={self.sampling_rate})"
        )