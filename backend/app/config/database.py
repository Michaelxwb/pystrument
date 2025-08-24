"""
数据库连接配置
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
from typing import Optional
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)

# 全局数据库连接实例
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_database = None
redis_client: Optional[aioredis.Redis] = None


async def init_database():
    """初始化数据库连接"""
    global mongodb_client, mongodb_database, redis_client
    
    try:
        # 初始化MongoDB连接
        logger.info("正在连接MongoDB...")
        mongodb_client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000
        )
        
        # 测试MongoDB连接
        await mongodb_client.admin.command('ping')
        mongodb_database = mongodb_client[settings.mongodb_database]
        logger.info("MongoDB连接成功")
        
        # 初始化Redis连接
        logger.info("正在连接Redis...")
        redis_client = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20
        )
        
        # 测试Redis连接
        await redis_client.ping()
        logger.info("Redis连接成功")
        
        # 创建索引
        await create_indexes()
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


async def close_database():
    """关闭数据库连接"""
    global mongodb_client, redis_client
    
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB连接已关闭")
    
    if redis_client:
        await redis_client.close()
        logger.info("Redis连接已关闭")


async def create_indexes():
    """创建数据库索引"""
    if not mongodb_database:
        return
    
    try:
        # 项目集合索引
        projects_collection = mongodb_database.projects
        await projects_collection.create_index("project_key", unique=True)
        await projects_collection.create_index("name")
        await projects_collection.create_index("status")
        
        # 性能记录集合索引
        performance_collection = mongodb_database.performance_records
        await performance_collection.create_index("project_key")
        await performance_collection.create_index("trace_id", unique=True)
        await performance_collection.create_index([("project_key", 1), ("timestamp", -1)])
        await performance_collection.create_index("request_info.path")
        await performance_collection.create_index("performance_metrics.total_duration")
        
        # 函数调用集合索引
        function_calls_collection = mongodb_database.function_calls
        await function_calls_collection.create_index("trace_id")
        await function_calls_collection.create_index("call_id", unique=True)
        await function_calls_collection.create_index([("trace_id", 1), ("call_order", 1)])
        
        # AI分析结果集合索引
        analysis_collection = mongodb_database.ai_analysis_results
        await analysis_collection.create_index("project_key")
        await analysis_collection.create_index("trace_id")
        await analysis_collection.create_index("status")
        await analysis_collection.create_index([("project_key", 1), ("created_at", -1)])
        
        # 系统配置集合索引
        config_collection = mongodb_database.system_config
        await config_collection.create_index("config_key", unique=True)
        await config_collection.create_index("category")
        
        logger.info("数据库索引创建完成")
        
    except Exception as e:
        logger.error(f"创建索引失败: {str(e)}")


def get_database():
    """获取数据库实例"""
    return mongodb_database


def get_redis():
    """获取Redis实例"""
    return redis_client