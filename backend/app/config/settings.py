"""
应用配置管理
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"
    api_version: str = "v1"
    
    # 数据库配置
    mongodb_url: str = "mongodb://admin:admin123@127.0.0.1:27017/?authSource=admin"
    # mongodb_url: str = "mongodb://192.168.1.7:37017/pystrument"
    # mongodb_url: str = "mongodb://34.tcp.cpolar.top:10795/pystrument"
    mongodb_database: str = "pystrument"
    redis_url: str = "redis://:redis123@localhost:6379/0"
    
    # AI服务配置
    openai_api_key: str = ""
    aliyun_qianwen_api_key: str = ""
    ai_service_timeout: int = 30
    
    # 监控配置
    default_sampling_rate: float = 0.3
    max_batch_size: int = 100
    async_send_timeout: int = 5
    
    # 安全配置
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080"
    ]
    max_request_size: int = 10485760  # 10MB
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "/var/log/pystrument/app.log"
    
    # Celery配置
    celery_broker_url: str = "redis://:redis123@localhost:6379/1"
    celery_result_backend: str = "redis://:redis123@localhost:6379/2"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建配置实例
settings = Settings()