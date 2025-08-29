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
    ALIYUN_QIANWEN = "aliyun_qianwen"


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
        # 加载环境变量
        self._load_env_vars()
        
        self.config_file = config_file or "ai_config.yaml"
        self.services: Dict[str, AIServiceConfig] = {}
        self.default_service: str = "openai"
        self.analysis_templates: Dict[str, str] = {}
        
        self._load_config()
    
    def _load_env_vars(self):
        """加载环境变量"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.info("环境变量加载成功")
        except ImportError:
            logger.warning("python-dotenv未安装，跳过环境变量加载")
        except Exception as e:
            logger.error(f"加载环境变量失败: {str(e)}")
    
    def _load_config(self):
        """加载配置"""
        try:
            # 从环境变量加载
            self._load_from_env()
            
            # 从配置文件加载（会覆盖环境变量中的同名配置）
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
                enabled=True,
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
                enabled=True,
                api_key=azure_key,
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
                headers={
                    "api-key": azure_key
                }
            )
        
        # 阿里千问配置
        aliyun_key = os.getenv("ALIYUN_QIANWEN_API_KEY")
        if aliyun_key:
            self.services["aliyun_qianwen"] = AIServiceConfig(
                provider=AIProvider.ALIYUN_QIANWEN,
                enabled=True,
                api_key=aliyun_key,
                endpoint=os.getenv("ALIYUN_QIANWEN_ENDPOINT", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"),
                model=os.getenv("ALIYUN_QIANWEN_MODEL", "qwen-turbo"),
                max_tokens=int(os.getenv("ALIYUN_QIANWEN_MAX_TOKENS", "2000")),
                temperature=float(os.getenv("ALIYUN_QIANWEN_TEMPERATURE", "0.7")),
                headers={
                    "Authorization": f"Bearer {aliyun_key}",
                    "Content-Type": "application/json"
                }
            )
        
        # 自定义AI服务配置
        custom_endpoint = os.getenv("CUSTOM_AI_ENDPOINT")
        if custom_endpoint:
            self.services["custom"] = AIServiceConfig(
                provider=AIProvider.CUSTOM,
                enabled=True,
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
                
                # 处理API密钥中的环境变量替换
                api_key = service_config.get("api_key")
                if isinstance(api_key, str) and api_key.startswith("${") and api_key.endswith("}"):
                    env_var_name = api_key[2:-1]
                    api_key = os.getenv(env_var_name, api_key)
                
                # 处理headers中的环境变量替换
                headers = service_config.get("headers", {})
                processed_headers = {}
                for header_name, header_value in headers.items():
                    if isinstance(header_value, str):
                        # 处理完整的环境变量替换 ${VAR_NAME}
                        if header_value.startswith("${") and header_value.endswith("}"):
                            env_var_name = header_value[2:-1]
                            actual_value = os.getenv(env_var_name, header_value)
                            processed_headers[header_name] = actual_value
                            logger.debug(f"完整替换环境变量 {env_var_name} -> {actual_value}")
                        # 处理包含环境变量的字符串 Bearer ${VAR_NAME}
                        elif "${" in header_value and "}" in header_value:
                            # 查找所有环境变量占位符
                            import re
                            pattern = r'\$\{([^}]+)\}'
                            matches = re.findall(pattern, header_value)
                            processed_value = header_value
                            for env_var_name in matches:
                                env_value = os.getenv(env_var_name, f"${{{env_var_name}}}")
                                processed_value = processed_value.replace(f"${{{env_var_name}}}", env_value)
                                logger.debug(f"部分替换环境变量 {env_var_name} -> {env_value}")
                            processed_headers[header_name] = processed_value
                        else:
                            processed_headers[header_name] = header_value
                    else:
                        processed_headers[header_name] = header_value
                
                # 记录处理后的headers用于调试
                logger.debug(f"服务 {service_name} 处理后的headers: {processed_headers}")
                
                self.services[service_name] = AIServiceConfig(
                    provider=provider,
                    enabled=service_config.get("enabled", True),
                    model=service_config.get("model", "gpt-4"),
                    api_key=api_key,
                    endpoint=service_config.get("endpoint"),
                    timeout=service_config.get("timeout", 30),
                    max_tokens=service_config.get("max_tokens", 4000),
                    temperature=service_config.get("temperature", 0.3),
                    headers=processed_headers,
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
    
    async def _load_from_database(self, db):
        """从数据库加载配置"""
        try:
            # 从系统配置集合获取设置
            settings_doc = await db.system_config.find_one({"config_key": "platform_settings"})
            
            if settings_doc and "config_value" in settings_doc:
                config_value = settings_doc["config_value"]
                
                # 检查AI配置是否存在
                if "ai" in config_value:
                    ai_config = config_value["ai"]
                    
                    # 更新默认服务
                    default_service = ai_config.get("defaultService")
                    if default_service:
                        # 映射前端服务名称到后端服务名称
                        service_mapping = {
                            "openai-gpt4": "openai",
                            "openai-gpt3.5": "openai",
                            "aliyun_qianwen": "aliyun_qianwen"
                        }
                        mapped_service = service_mapping.get(default_service, default_service)
                        if mapped_service in self.services:
                            self.default_service = mapped_service
                    
                    # 更新API密钥
                    api_key = ai_config.get("apiKey")
                    if api_key and self.default_service in self.services:
                        self.services[self.default_service].api_key = api_key
                    
                    logger.info(f"从数据库加载AI配置成功，默认服务: {self.default_service}")
            
        except Exception as e:
            logger.error(f"从数据库加载AI配置失败: {str(e)}")
    
    def get_service(self, service_name: Optional[str] = None) -> Optional[AIServiceConfig]:
        """获取AI服务配置"""
        service_name = service_name or self.default_service
        return self.services.get(service_name)
    
    async def get_service_async(self, service_name: Optional[str] = None, db=None) -> Optional[AIServiceConfig]:
        """获取AI服务配置（支持从数据库动态加载）"""
        # 如果提供了数据库连接，则从数据库加载最新配置
        if db:
            await self._load_from_database(db)
        
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