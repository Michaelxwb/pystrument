#!/usr/bin/env python3
"""
测试阿里千问AI服务配置
"""
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

print("环境变量检查:")
print(f"ALIYUN_QIANWEN_API_KEY: {os.getenv('ALIYUN_QIANWEN_API_KEY')}")

# 测试环境变量替换
test_value = "${ALIYUN_QIANWEN_API_KEY}"
if test_value.startswith("${") and test_value.endswith("}"):
    env_var_name = test_value[2:-1]
    actual_value = os.getenv(env_var_name, test_value)
    print(f"替换后的值: {actual_value}")

from app.services.ai_config import AIConfigManager


def test_qwen_config():
    """测试阿里千问配置加载"""
    print("\n测试阿里千问AI服务配置加载...")
    
    # 创建配置管理器实例
    config_manager = AIConfigManager("ai_config.yaml")
    
    print(f"默认服务: {config_manager.default_service}")
    
    # 测试获取阿里千问服务
    print("\n测试获取阿里千问服务:")
    qwen_service = config_manager.get_service("aliyun_qianwen")
    if qwen_service:
        print(f"  服务存在: 是")
        print(f"  提供商: {qwen_service.provider.value}")
        print(f"  启用: {qwen_service.enabled}")
        print(f"  模型: {qwen_service.model}")
        print(f"  端点: {qwen_service.endpoint}")
        print(f"  API密钥: {'*' * len(qwen_service.api_key) if qwen_service.api_key else 'None'}")
        print(f"  Headers: {qwen_service.headers}")
        if "Authorization" in qwen_service.headers:
            auth_value = qwen_service.headers["Authorization"]
            print(f"  Authorization头: {auth_value}")
        print(f"  最大令牌数: {qwen_service.max_tokens}")
        print(f"  温度: {qwen_service.temperature}")
    else:
        print("  服务不存在")
    
    # 测试获取所有启用的服务
    print("\n所有启用的AI服务:")
    enabled_services = config_manager.get_enabled_services()
    for name, service in enabled_services.items():
        print(f"  {name}: {service.provider.value} ({service.model})")


if __name__ == "__main__":
    test_qwen_config()