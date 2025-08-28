"""
项目管理相关API路由
"""
from fastapi import APIRouter, HTTPException, Path, Depends, Query, Body
from typing import Dict, Any, Optional, List
import logging
import uuid
from datetime import datetime, timedelta

from app.utils.response import success_response, error_response
from app.utils.database import get_database

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def list_projects(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页记录数"),
    name: Optional[str] = Query(None, description="项目名称模糊搜索"),
    status: Optional[str] = Query(None, description="状态过滤"),
    framework: Optional[str] = Query(None, description="框架过滤"),
    db = Depends(get_database)
):
    """获取项目列表"""
    logger.info(f"获取项目列表, 页码: {page}, 大小: {size}")
    
    # 构建查询条件
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}  # 模糊搜索，不区分大小写
    if status:
        query["status"] = status
    if framework:
        query["framework"] = framework
    
    # 计算总数
    total = await db.projects.count_documents(query)
    
    # 获取分页数据
    skip = (page - 1) * size
    cursor = db.projects.find(query).sort("created_at", -1).skip(skip).limit(size)
    
    projects = []
    async for project in cursor:
        # 将MongoDB对象转换为可序列化的字典
        project_dict = {k: v for k, v in project.items() if k != "_id"}
        
        # 格式化日期时间字段
        for date_field in ["created_at", "updated_at"]:
            if date_field in project_dict:
                project_dict[date_field] = project_dict[date_field].isoformat()
        
        projects.append(project_dict)
    
    return success_response({
        "projects": projects,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    })


@router.get("/{project_key}")
async def get_project(
    project_key: str = Path(..., description="项目标识"),
    db = Depends(get_database)
):
    """获取项目详情"""
    logger.info(f"获取项目详情: {project_key}")
    
    project = await db.projects.find_one({"project_key": project_key})
    if not project:
        logger.warning(f"项目不存在: {project_key}")
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_key}")
    
    # 将MongoDB对象转换为可序列化的字典
    result = {k: v for k, v in project.items() if k != "_id"}
    
    # 格式化日期时间字段
    for date_field in ["created_at", "updated_at"]:
        if date_field in result:
            result[date_field] = result[date_field].isoformat()
    
    return success_response(result)


@router.post("/")
async def create_project(
    project_data: dict = Body(...),
    db = Depends(get_database)
):
    """创建项目"""
    logger.info(f"创建项目: {project_data.get('name')}")
    
    # 生成项目标识
    project_key = project_data.get("project_key") or f"proj_{uuid.uuid4().hex[:8]}"
    
    # 检查项目标识是否已存在
    existing_project = await db.projects.find_one({"project_key": project_key})
    if existing_project:
        logger.warning(f"项目标识已存在: {project_key}")
        raise HTTPException(status_code=400, detail=f"项目标识已存在: {project_key}")
    
    # 创建项目记录
    project = {
        "project_key": project_key,
        "name": project_data.get("name"),
        "description": project_data.get("description"),
        "framework": project_data.get("framework"),
        "api_key": project_data.get("api_key") or str(uuid.uuid4()),
        "status": project_data.get("status", "active"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.projects.insert_one(project)
    
    # 将MongoDB对象转换为可序列化的字典
    result = {k: v for k, v in project.items() if k != "_id"}
    
    # 格式化日期时间字段
    for date_field in ["created_at", "updated_at"]:
        result[date_field] = result[date_field].isoformat()
    
    return success_response(result)


@router.put("/{project_key}")
async def update_project(
    project_key: str = Path(..., description="项目标识"),
    project_data: dict = Body(...),
    db = Depends(get_database)
):
    """更新项目"""
    logger.info(f"更新项目: {project_key}")
    
    # 检查项目是否存在
    project = await db.projects.find_one({"project_key": project_key})
    if not project:
        logger.warning(f"项目不存在: {project_key}")
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_key}")
    
    # 更新项目记录
    update_data = {
        "updated_at": datetime.utcnow()
    }
    
    for field in ["name", "description", "framework", "api_key", "status"]:
        if field in project_data:
            update_data[field] = project_data[field]
    
    await db.projects.update_one(
        {"project_key": project_key},
        {"$set": update_data}
    )
    
    # 获取更新后的项目
    updated_project = await db.projects.find_one({"project_key": project_key})
    
    # 将MongoDB对象转换为可序列化的字典
    result = {k: v for k, v in updated_project.items() if k != "_id"}
    
    # 格式化日期时间字段
    for date_field in ["created_at", "updated_at"]:
        result[date_field] = result[date_field].isoformat()
    
    return success_response(result)


@router.delete("/{project_key}")
async def delete_project(
    project_key: str = Path(..., description="项目标识"),
    db = Depends(get_database)
):
    """删除项目"""
    logger.info(f"删除项目: {project_key}")
    
    # 检查项目是否存在
    project = await db.projects.find_one({"project_key": project_key})
    if not project:
        logger.warning(f"项目不存在: {project_key}")
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_key}")
    
    # 删除项目
    await db.projects.delete_one({"project_key": project_key})
    
    return success_response({"message": "项目删除成功"})


@router.get("/{project_key}/stats")
async def get_project_stats(
    project_key: str = Path(..., description="项目标识"),
    db = Depends(get_database)
):
    """获取项目统计数据"""
    logger.info(f"获取项目统计数据: {project_key}")
    
    # 检查项目是否存在
    project = await db.projects.find_one({"project_key": project_key})
    if not project:
        logger.warning(f"项目不存在: {project_key}")
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_key}")
    
    # 查询性能记录总数
    performance_count = await db.performance_records.count_documents({"project_key": project_key})
    
    # 查询最近24小时的请求数
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    today_requests = await db.performance_records.count_documents({
        "project_key": project_key,
        "timestamp": {"$gte": yesterday}
    })
    
    # 查询平均响应时间
    pipeline = [
        {"$match": {"project_key": project_key}},
        {"$group": {
            "_id": None,
            "avg_response_time": {"$avg": "$performance_metrics.total_duration"}
        }}
    ]
    avg_result = await db.performance_records.aggregate(pipeline).to_list(1)
    avg_response_time = avg_result[0]["avg_response_time"] if avg_result else 0
    
    # 查询错误率
    error_count = await db.performance_records.count_documents({
        "project_key": project_key,
        "response_info.status_code": {"$gte": 400}
    })
    
    error_rate = (error_count / performance_count * 100) if performance_count > 0 else 0
    
    # 计算性能评分
    performance_score = 100 - (error_rate * 0.5) - min(avg_response_time * 1000 / 10, 50)
    
    return success_response({
        "project_key": project_key,
        "name": project.get("name"),
        "total_records": performance_count,
        "today_requests": today_requests,
        "avg_response_time": avg_response_time,
        "error_rate": error_rate,
        "performance_score": performance_score
    })