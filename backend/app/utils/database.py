"""
数据库工具模块
"""
import asyncio
from typing import Optional, Dict, Any, List
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis

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
        await projects_collection.create_index("created_at")
        await projects_collection.create_index("last_activity")
        
        # 性能记录集合索引
        performance_collection = mongodb_database.performance_records
        await performance_collection.create_index("project_key")
        await performance_collection.create_index("trace_id", unique=True)
        await performance_collection.create_index([("project_key", 1), ("timestamp", -1)])
        await performance_collection.create_index("request_info.path")
        await performance_collection.create_index("request_info.method")
        await performance_collection.create_index("response_info.status_code")
        await performance_collection.create_index("performance_metrics.total_duration")
        await performance_collection.create_index("timestamp")
        
        # 函数调用集合索引
        function_calls_collection = mongodb_database.function_calls
        await function_calls_collection.create_index("trace_id")
        await function_calls_collection.create_index("call_id", unique=True)
        await function_calls_collection.create_index([("trace_id", 1), ("call_context.call_order", 1)])
        await function_calls_collection.create_index("function_info.name")
        await function_calls_collection.create_index("execution_info.duration")
        await function_calls_collection.create_index("performance_tags")
        
        # AI分析结果集合索引
        analysis_collection = mongodb_database.ai_analysis_results
        await analysis_collection.create_index("project_key")
        await analysis_collection.create_index("analysis_id", unique=True)
        await analysis_collection.create_index("trace_id")
        await analysis_collection.create_index("status")
        await analysis_collection.create_index([("project_key", 1), ("created_at", -1)])
        await analysis_collection.create_index("analysis_type")
        
        # 系统配置集合索引
        config_collection = mongodb_database.system_config
        await config_collection.create_index("config_key", unique=True)
        await config_collection.create_index("category")
        await config_collection.create_index("is_active")
        
        logger.info("数据库索引创建完成")
        
    except Exception as e:
        logger.error(f"创建索引失败: {str(e)}")


def get_database():
    """获取数据库实例"""
    return mongodb_database


def get_redis():
    """获取Redis实例"""
    return redis_client


class DatabaseUtils:
    """数据库工具类"""
    
    @staticmethod
    async def paginate_query(collection, query: Dict[str, Any], page: int, size: int, sort_field: str = "created_at", sort_order: int = -1):
        """分页查询工具"""
        try:
            # 计算总数
            total = await collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * size
            cursor = collection.find(query).skip(skip).limit(size).sort(sort_field, sort_order)
            
            documents = []
            async for doc in cursor:
                doc.pop("_id", None)  # 移除MongoDB的_id字段
                documents.append(doc)
            
            return documents, total
            
        except Exception as e:
            logger.error(f"分页查询失败: {str(e)}")
            raise
    
    @staticmethod
    async def aggregate_with_pagination(collection, pipeline: List[Dict[str, Any]], page: int, size: int):
        """聚合查询分页工具"""
        try:
            # 添加分页阶段
            skip = (page - 1) * size
            paginated_pipeline = pipeline + [
                {"$skip": skip},
                {"$limit": size}
            ]
            
            # 执行聚合查询
            cursor = collection.aggregate(paginated_pipeline)
            documents = []
            async for doc in cursor:
                doc.pop("_id", None)
                documents.append(doc)
            
            # 计算总数（需要单独的聚合查询）
            count_pipeline = pipeline + [{"$count": "total"}]
            count_cursor = collection.aggregate(count_pipeline)
            count_result = await count_cursor.to_list(1)
            total = count_result[0]["total"] if count_result else 0
            
            return documents, total
            
        except Exception as e:
            logger.error(f"聚合分页查询失败: {str(e)}")
            raise
    
    @staticmethod
    async def batch_insert(collection, documents: List[Dict[str, Any]], batch_size: int = 1000):
        """批量插入工具"""
        try:
            if not documents:
                return 0
            
            inserted_count = 0
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                result = await collection.insert_many(batch, ordered=False)
                inserted_count += len(result.inserted_ids)
            
            return inserted_count
            
        except Exception as e:
            logger.error(f"批量插入失败: {str(e)}")
            raise
    
    @staticmethod
    async def batch_update(collection, updates: List[Dict[str, Any]], batch_size: int = 1000):
        """批量更新工具"""
        try:
            if not updates:
                return 0
            
            updated_count = 0
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]
                
                # 构建批量操作
                bulk_operations = []
                for update_op in batch:
                    bulk_operations.append({
                        "update_one": {
                            "filter": update_op["filter"],
                            "update": update_op["update"],
                            "upsert": update_op.get("upsert", False)
                        }
                    })
                
                # 执行批量操作
                if bulk_operations:
                    result = await collection.bulk_write(bulk_operations, ordered=False)
                    updated_count += result.modified_count
            
            return updated_count
            
        except Exception as e:
            logger.error(f"批量更新失败: {str(e)}")
            raise


class RedisUtils:
    """Redis工具类"""
    
    @staticmethod
    async def cache_get(key: str, default=None):
        """获取缓存"""
        try:
            redis = get_redis()
            if redis:
                value = await redis.get(key)
                return value if value is not None else default
            return default
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            return default
    
    @staticmethod
    async def cache_set(key: str, value: Any, expire: int = 3600):
        """设置缓存"""
        try:
            redis = get_redis()
            if redis:
                await redis.setex(key, expire, value)
                return True
            return False
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")
            return False
    
    @staticmethod
    async def cache_delete(key: str):
        """删除缓存"""
        try:
            redis = get_redis()
            if redis:
                await redis.delete(key)
                return True
            return False
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            return False
    
    @staticmethod
    async def cache_exists(key: str) -> bool:
        """检查缓存是否存在"""
        try:
            redis = get_redis()
            if redis:
                return await redis.exists(key) > 0
            return False
        except Exception as e:
            logger.error(f"检查缓存存在性失败: {str(e)}")
            return False
    
    @staticmethod
    async def increment_counter(key: str, expire: int = 3600) -> int:
        """递增计数器"""
        try:
            redis = get_redis()
            if redis:
                count = await redis.incr(key)
                if count == 1:  # 首次设置
                    await redis.expire(key, expire)
                return count
            return 0
        except Exception as e:
            logger.error(f"递增计数器失败: {str(e)}")
            return 0