"""
AI服务配置管理
"""
import os
import yaml
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI服务提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"
    AZURE_OPENAI = "azure_openai"
    HUGGINGFACE = "huggingface"


@dataclass
class AIServiceConfig:
    """AI服务配置"""
    provider: AIProvider
    enabled: bool = True
    
    # 通用配置
    model: str = "gpt-4"
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    timeout: int = 30
    max_tokens: int = 4000
    temperature: float = 0.3
    
    # 特定配置
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # 成本控制
    cost_per_token: float = 0.0
    daily_limit: float = 100.0  # 每日成本限制（美元）


class AIConfigManager:
    """AI配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "ai_config.yaml"
        self.services: Dict[str, AIServiceConfig] = {}
        self.default_service: str = "openai"
        self.analysis_templates: Dict[str, str] = {}
        
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        try:
            # 从环境变量加载
            self._load_from_env()
            
            # 从配置文件加载
            if os.path.exists(self.config_file):
                self._load_from_file()
            else:
                self._create_default_config()
                
        except Exception as e:
            logger.error(f"加载AI配置失败: {str(e)}")
            self._create_default_config()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        # OpenAI配置
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.services["openai"] = AIServiceConfig(
                provider=AIProvider.OPENAI,
                api_key=openai_key,
                endpoint=os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1/chat/completions"),
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "4000")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
            )
        
        # Azure OpenAI配置
        azure_key = os.getenv("AZURE_OPENAI_KEY")
        if azure_key:
            self.services["azure_openai"] = AIServiceConfig(
                provider=AIProvider.AZURE_OPENAI,
                api_key=azure_key,
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
                headers={
                    "api-key": azure_key
                }
            )
        
        # 自定义AI服务配置
        custom_endpoint = os.getenv("CUSTOM_AI_ENDPOINT")
        if custom_endpoint:
            self.services["custom"] = AIServiceConfig(
                provider=AIProvider.CUSTOM,
                endpoint=custom_endpoint,
                api_key=os.getenv("CUSTOM_AI_TOKEN"),
                model=os.getenv("CUSTOM_AI_MODEL", "custom-model"),
                headers={
                    "Authorization": f"Bearer {os.getenv('CUSTOM_AI_TOKEN', '')}"
                }
            )
        
        # 默认服务
        self.default_service = os.getenv("DEFAULT_AI_SERVICE", "openai")
    
    def _load_from_file(self):
        """从配置文件加载"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            # 解析AI服务配置
            ai_services = config_data.get("ai_services", {})
            for service_name, service_config in ai_services.items():
                provider = AIProvider(service_config.get("provider", "custom"))
                
                self.services[service_name] = AIServiceConfig(
                    provider=provider,
                    enabled=service_config.get("enabled", True),
                    model=service_config.get("model", "gpt-4"),
                    api_key=service_config.get("api_key"),
                    endpoint=service_config.get("endpoint"),
                    timeout=service_config.get("timeout", 30),
                    max_tokens=service_config.get("max_tokens", 4000),
                    temperature=service_config.get("temperature", 0.3),
                    headers=service_config.get("headers", {}),
                    params=service_config.get("params", {}),
                    max_retries=service_config.get("max_retries", 3),
                    retry_delay=service_config.get("retry_delay", 1.0),
                    cost_per_token=service_config.get("cost_per_token", 0.0),
                    daily_limit=service_config.get("daily_limit", 100.0)
                )
            
            # 解析默认服务
            self.default_service = config_data.get("default_service", "openai")
            
            # 解析分析模板
            self.analysis_templates = config_data.get("analysis_templates", {})
            
        except Exception as e:
            logger.error(f"从文件加载AI配置失败: {str(e)}")
    
    def _create_default_config(self):
        """创建默认配置"""
        self.services = {
            "openai": AIServiceConfig(
                provider=AIProvider.OPENAI,
                enabled=bool(os.getenv("OPENAI_API_KEY")),
                api_key=os.getenv("OPENAI_API_KEY"),
                endpoint="https://api.openai.com/v1/chat/completions",
                model="gpt-4",
                max_tokens=4000,
                temperature=0.3
            )
        }
        
        self.analysis_templates = {
            "performance_analysis": """
请分析以下Python Web应用的性能数据：

## 基本信息
- 请求路径: {request_path}
- 请求方法: {request_method}
- 响应状态: {status_code}
- 框架: {framework}

## 性能指标
- 总耗时: {total_duration}秒
- CPU时间: {cpu_time}秒
- 峰值内存: {memory_peak}MB
- 函数调用数: {function_count}
- 慢函数数量: {slow_function_count}

## 最慢的函数调用
{slow_functions}

请提供：
1. 性能评分（0-100分）
2. 主要性能瓶颈分析
3. 具体的优化建议
4. 潜在风险评估

请以JSON格式返回结构化的分析结果。
""",
            
            "bottleneck_detection": """
识别以下调用链路中的性能瓶颈：

{function_call_tree}

请分析：
1. 哪些函数是主要的性能瓶颈
2. 瓶颈的类型（数据库、计算、I/O等）
3. 影响程度评估
4. 优化优先级建议
""",
            
            "optimization_suggestions": """
基于以下性能数据，提供具体的优化建议：

{performance_data}

请提供：
1. 数据库优化建议
2. 代码算法优化
3. 缓存策略建议
4. 架构改进建议
5. 预期的性能提升效果
"""
        }
        
        # 保存默认配置
        self.save_config()
    
    def get_service(self, service_name: Optional[str] = None) -> Optional[AIServiceConfig]:
        """获取AI服务配置"""
        service_name = service_name or self.default_service
        return self.services.get(service_name)
    
    def get_enabled_services(self) -> Dict[str, AIServiceConfig]:
        """获取启用的AI服务"""
        return {name: config for name, config in self.services.items() if config.enabled}
    
    def add_service(self, name: str, config: AIServiceConfig):
        """添加AI服务"""
        self.services[name] = config
    
    def remove_service(self, name: str):
        """移除AI服务"""
        if name in self.services:
            del self.services[name]
    
    def set_default_service(self, service_name: str):
        """设置默认AI服务"""
        if service_name in self.services:
            self.default_service = service_name
        else:
            raise ValueError(f"AI服务 '{service_name}' 不存在")
    
    def get_template(self, template_name: str) -> Optional[str]:
        """获取分析模板"""
        return self.analysis_templates.get(template_name)
    
    def add_template(self, name: str, template: str):
        """添加分析模板"""
        self.analysis_templates[name] = template
    
    def save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                "default_service": self.default_service,
                "ai_services": {},
                "analysis_templates": self.analysis_templates
            }
            
            # 转换服务配置
            for name, service in self.services.items():
                config_data["ai_services"][name] = {
                    "provider": service.provider.value,
                    "enabled": service.enabled,
                    "model": service.model,
                    "api_key": service.api_key,
                    "endpoint": service.endpoint,
                    "timeout": service.timeout,
                    "max_tokens": service.max_tokens,
                    "temperature": service.temperature,
                    "headers": service.headers,
                    "params": service.params,
                    "max_retries": service.max_retries,
                    "retry_delay": service.retry_delay,
                    "cost_per_token": service.cost_per_token,
                    "daily_limit": service.daily_limit
                }
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"AI配置已保存到: {self.config_file}")
            
        except Exception as e:
            logger.error(f"保存AI配置失败: {str(e)}")
    
    def validate_service(self, service_name: str) -> bool:
        """验证AI服务配置"""
        service = self.get_service(service_name)
        if not service:
            return False
        
        # 检查必需的配置
        if service.provider in [AIProvider.OPENAI, AIProvider.AZURE_OPENAI]:
            return bool(service.api_key)
        elif service.provider == AIProvider.CUSTOM:
            return bool(service.endpoint)
        
        return True
    
    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有服务状态"""
        status = {}
        
        for name, service in self.services.items():
            status[name] = {
                "provider": service.provider.value,
                "enabled": service.enabled,
                "model": service.model,
                "configured": self.validate_service(name),
                "is_default": name == self.default_service
            }
        
        return status


# 全局AI配置管理器实例
ai_config_manager = AIConfigManager()