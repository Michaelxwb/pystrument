"""
初始化数据库脚本
"""
import asyncio
import logging
from datetime import datetime, timedelta
import uuid
import random

from app.utils.database import get_database, init_database, close_database

logger = logging.getLogger(__name__)

# 示例项目数据
SAMPLE_PROJECTS = [
    {
        "project_key": "proj_ecommerce",
        "name": "电商系统",
        "description": "在线电子商务平台，包含商品、订单、用户等核心功能",
        "framework": "FastAPI",
        "api_key": str(uuid.uuid4()),
        "status": "active",
        "created_at": datetime.utcnow() - timedelta(days=30),
        "updated_at": datetime.utcnow() - timedelta(days=1)
    },
    {
        "project_key": "proj_usercenter",
        "name": "用户中心",
        "description": "用户管理与认证系统，支持多种登录方式",
        "framework": "Flask",
        "api_key": str(uuid.uuid4()),
        "status": "active",
        "created_at": datetime.utcnow() - timedelta(days=20),
        "updated_at": datetime.utcnow() - timedelta(days=2)
    },
    {
        "project_key": "proj_orderservice",
        "name": "订单服务",
        "description": "订单处理与支付系统，支持多种支付方式",
        "framework": "Django",
        "api_key": str(uuid.uuid4()),
        "status": "active",
        "created_at": datetime.utcnow() - timedelta(days=15),
        "updated_at": datetime.utcnow() - timedelta(days=3)
    }
]

# 创建一些分析结果
async def create_sample_analysis_records(db):
    logger.info("创建示例分析记录...")
    
    # 检查是否已有分析记录
    count = await db.ai_analysis_results.count_documents({})
    if count > 0:
        logger.info(f"已存在 {count} 条分析记录，跳过")
        return
    
    analysis_types = ["ai_analysis", "performance_report", "trend_analysis"]
    ai_services = ["OpenAI", "Local", "Custom"]
    statuses = ["PENDING", "IN_PROGRESS", "COMPLETED", "FAILURE", "CANCELED"]
    
    for project in SAMPLE_PROJECTS:
        project_key = project["project_key"]
        
        # 为每个项目创建5-10条分析记录
        num_records = random.randint(5, 10)
        for i in range(num_records):
            # 随机选择状态和创建时间
            status = random.choice(statuses)
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30), 
                                                    hours=random.randint(0, 23), 
                                                    minutes=random.randint(0, 59))
            updated_at = created_at + timedelta(minutes=random.randint(1, 30))
            
            # 创建分析ID和任务ID
            task_id = str(uuid.uuid4())
            analysis_id = f"analysis_{project_key}_{task_id[:8]}"
            
            # 随机选择分析类型和AI服务
            analysis_type = random.choice(analysis_types)
            ai_service = random.choice(ai_services)
            
            # 创建分析记录
            analysis_record = {
                "analysis_id": analysis_id,
                "performance_record_id": f"trace_{uuid.uuid4().hex[:12]}",
                "project_key": project_key,
                "analysis_type": analysis_type,
                "ai_service": ai_service,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
                "task_id": task_id,
                "priority": random.choice(["high", "normal", "low"])
            }
            
            # 如果状态是已完成，添加结果
            if status == "COMPLETED":
                analysis_record["results"] = {
                    "summary": get_random_summary(),
                    "performance_score": random.randint(50, 95),
                    "bottlenecks": get_random_bottlenecks(),
                    "recommendations": get_random_recommendations()
                }
            
            await db.ai_analysis_results.insert_one(analysis_record)
    
    logger.info("示例分析记录创建完成")

# 随机生成分析摘要
def get_random_summary():
    summaries = [
        "发现3个性能瓶颈，建议优化数据库查询",
        "系统整体性能良好，有少量优化空间",
        "关键API响应时间较长，建议添加缓存",
        "数据库查询过多，推荐合并请求",
        "发现内存使用量异常，可能存在内存泄漏",
        "CPU使用率过高，需优化计算密集操作",
        "文件I/O操作频繁，建议使用缓存",
        "网络请求延迟高，考虑使用连接池"
    ]
    return random.choice(summaries)

# 随机生成瓶颈列表
def get_random_bottlenecks():
    bottleneck_types = ["database", "computation", "memory", "io", "network"]
    bottleneck_descriptions = [
        "数据库查询耗时较长",
        "CPU计算密集操作效率低",
        "内存使用量异常增长",
        "文件读写操作频繁",
        "网络请求延迟高",
        "缓存命中率低",
        "并发处理能力不足",
        "资源竞争导致性能下降"
    ]
    
    num_bottlenecks = random.randint(0, 3)
    bottlenecks = []
    
    for _ in range(num_bottlenecks):
        bottleneck = {
            "type": random.choice(bottleneck_types),
            "severity": random.choice(["high", "medium", "low"]),
            "function": f"function_{random.randint(1000, 9999)}",
            "description": random.choice(bottleneck_descriptions),
            "impact": random.uniform(0.1, 0.9),
            "recommendations": [
                "优化SQL查询",
                "添加索引",
                "使用缓存",
                "减少I/O操作",
                "优化算法"
            ][:random.randint(1, 3)]
        }
        bottlenecks.append(bottleneck)
    
    return bottlenecks

# 随机生成建议列表
def get_random_recommendations():
    recommendations = [
        "优化数据库查询",
        "添加适当的索引",
        "实现数据缓存",
        "减少不必要的API调用",
        "优化循环中的计算",
        "使用连接池",
        "实现请求合并",
        "增加服务器资源",
        "优化代码结构",
        "减少不必要的日志记录"
    ]
    
    num_recommendations = random.randint(2, 5)
    return random.sample(recommendations, num_recommendations)

# 创建样本项目
async def create_sample_projects(db):
    logger.info("创建示例项目...")
    
    # 检查是否已有项目
    count = await db.projects.count_documents({})
    if count > 0:
        logger.info(f"已存在 {count} 个项目，跳过")
        return
    
    # 创建示例项目
    for project in SAMPLE_PROJECTS:
        await db.projects.insert_one(project)
    
    logger.info(f"已创建 {len(SAMPLE_PROJECTS)} 个示例项目")

# 主函数
async def init_sample_data():
    logger.info("开始初始化示例数据...")
    
    # 初始化数据库连接
    await init_database()
    
    # 获取数据库连接
    db = await get_database()
    
    # 创建示例数据
    await create_sample_projects(db)
    await create_sample_analysis_records(db)
    
    # 关闭数据库连接
    await close_database()
    
    logger.info("示例数据初始化完成")

# 如果直接运行此脚本，则执行初始化
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_sample_data())