"""
AI分析相关API路由
"""
from fastapi import APIRouter, HTTPException, Path, Depends, Body, Query
from typing import Dict, Any, Optional, List
import logging
import uuid
from datetime import datetime, timedelta

from app.utils.response import success_response, error_response
from app.utils.database import get_database
from app.models.analysis import AnalysisRequest, TaskStatus, AnalysisRecord

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def list_analysis():
    """列出所有分析记录"""
    return success_response({
        "message": "AI分析服务正在开发中",
        "available_endpoints": [
            "/analyze/{performance_record_id}",
            "/batch-analyze",
            "/result/{analysis_id}",
            "/task-status/{task_id}",
            "/history",
            "/history/{project_key}"
        ]
    })


@router.post("/analyze/{performance_record_id}")
async def analyze_performance(
    performance_record_id: str = Path(..., description="性能记录ID"),
    request: AnalysisRequest = Body(...),
    db = Depends(get_database)
):
    """
    触发对单个性能记录的AI分析
    """
    logger.info(f"收到性能记录分析请求: {performance_record_id}, 服务: {request.ai_service}")
    
    # 检查性能记录是否存在
    performance_record = await db.performance_records.find_one({"trace_id": performance_record_id})
    if not performance_record:
        logger.warning(f"性能记录不存在: {performance_record_id}")
        raise HTTPException(status_code=404, detail=f"性能记录不存在: {performance_record_id}")
    
    # 创建分析任务
    task_id = str(uuid.uuid4())
    analysis_id = f"analysis_{performance_record_id}_{task_id[:8]}"
    
    # 创建任务状态记录
    task_status = {
        "task_id": task_id,
        "analysis_id": analysis_id,
        "status": "PENDING",
        "progress": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "estimated_completion": datetime.utcnow() + timedelta(minutes=2)
    }
    
    await db.analysis_tasks.insert_one(task_status)
    
    # 创建分析记录
    analysis_record = {
        "analysis_id": analysis_id,
        "performance_record_id": performance_record_id,
        "project_key": performance_record.get("project_key"),
        "ai_service": request.ai_service,
        "status": "PENDING",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "results": None,
        "task_id": task_id,
        "priority": request.priority
    }
    
    await db.analysis_records.insert_one(analysis_record)
    
    # 这里应该异步触发实际的分析任务
    # 在实际实现中，应该将任务发送到任务队列中处理
    # 为了简化示例，我们直接模拟分析任务已启动
    
    logger.info(f"已创建分析任务: {task_id}, 分析ID: {analysis_id}")
    
    # 模拟异步处理，立即更新任务状态为进行中
    await db.analysis_tasks.update_one(
        {"task_id": task_id},
        {"$set": {"status": "IN_PROGRESS", "progress": 10, "updated_at": datetime.utcnow()}}
    )
    
    # 为了演示，我们也更新分析记录状态
    await db.analysis_records.update_one(
        {"analysis_id": analysis_id},
        {"$set": {"status": "IN_PROGRESS", "updated_at": datetime.utcnow()}}
    )
    
    return success_response({
        "analysis_id": analysis_id,
        "task_id": task_id,
        "status": "PENDING",
        "estimated_completion": (datetime.utcnow() + timedelta(minutes=2)).isoformat()
    })


@router.get("/task-status/{task_id}")
async def get_task_status(
    task_id: str = Path(..., description="任务ID"),
    db = Depends(get_database)
):
    """获取任务状态"""
    logger.info(f"查询任务状态: {task_id}")
    
    task = await db.analysis_tasks.find_one({"task_id": task_id})
    if not task:
        logger.warning(f"任务不存在: {task_id}")
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    
    # 模拟任务进度更新
    # 在实际实现中，这应该反映真实的任务进度
    current_time = datetime.utcnow()
    created_time = task.get("created_at")
    
    # 如果任务是PENDING或IN_PROGRESS状态，并且已经过了一定时间，更新其状态
    if task.get("status") in ["PENDING", "IN_PROGRESS"]:
        time_diff = (current_time - created_time).total_seconds()
        
        # 模拟进度更新
        new_status = task.get("status")
        new_progress = task.get("progress", 0)
        
        if time_diff > 60:  # 如果已经过了60秒，将任务设为完成
            new_status = "SUCCESS"
            new_progress = 100
        elif time_diff > 30:  # 如果已经过了30秒，更新进度到75%
            new_progress = 75
        elif time_diff > 15:  # 如果已经过了15秒，更新进度到50%
            new_progress = 50
        elif time_diff > 5:   # 如果已经过了5秒，更新进度到25%
            new_progress = 25
        
        # 更新任务状态
        if new_status != task.get("status") or new_progress != task.get("progress"):
            await db.analysis_tasks.update_one(
                {"task_id": task_id},
                {"$set": {
                    "status": new_status, 
                    "progress": new_progress, 
                    "updated_at": current_time
                }}
            )
            
            # 如果任务完成，也更新相应的分析记录
            if new_status == "SUCCESS":
                analysis_record = await db.analysis_records.find_one({"task_id": task_id})
                if analysis_record:
                    # 生成一些模拟的分析结果
                    analysis_results = {
                        "summary": "这是一个演示分析结果，显示应用性能正常。",
                        "performance_score": 85,
                        "bottlenecks": [
                            {
                                "type": "database",
                                "description": "数据库查询耗时较长",
                                "recommendations": ["优化SQL查询", "添加索引"]
                            }
                        ],
                        "recommendations": [
                            "考虑添加缓存机制",
                            "优化慢查询"
                        ]
                    }
                    
                    await db.analysis_records.update_one(
                        {"analysis_id": analysis_record.get("analysis_id")},
                        {"$set": {
                            "status": "COMPLETED", 
                            "updated_at": current_time,
                            "results": analysis_results
                        }}
                    )
            
            # 重新获取更新后的任务
            task = await db.analysis_tasks.find_one({"task_id": task_id})
    
    # 格式化任务状态为API响应
    result = {
        "task_id": task.get("task_id"),
        "status": task.get("status"),
        "progress": task.get("progress", 0),
        "created_at": task.get("created_at").isoformat(),
        "updated_at": task.get("updated_at").isoformat(),
        "analysis_id": task.get("analysis_id")
    }
    
    if "estimated_completion" in task:
        result["estimated_completion"] = task["estimated_completion"].isoformat()
    
    return success_response(result)


@router.get("/result/{analysis_id}")
async def get_analysis_result(
    analysis_id: str = Path(..., description="分析ID"),
    db = Depends(get_database)
):
    """获取分析结果"""
    logger.info(f"获取分析结果: {analysis_id}")
    
    analysis = await db.analysis_records.find_one({"analysis_id": analysis_id})
    if not analysis:
        logger.warning(f"分析记录不存在: {analysis_id}")
        raise HTTPException(status_code=404, detail=f"分析记录不存在: {analysis_id}")
    
    # 将MongoDB对象转换为可序列化的字典
    result = {k: v for k, v in analysis.items() if k != "_id"}
    
    # 格式化日期时间字段
    for date_field in ["created_at", "updated_at"]:
        if date_field in result:
            result[date_field] = result[date_field].isoformat()
    
    return success_response(result)


@router.delete("/result/{analysis_id}")
async def delete_analysis_result(
    analysis_id: str = Path(..., description="分析ID"),
    db = Depends(get_database)
):
    """删除分析结果"""
    logger.info(f"删除分析结果: {analysis_id}")
    
    # 检查分析记录是否存在
    analysis = await db.analysis_records.find_one({"analysis_id": analysis_id})
    if not analysis:
        logger.warning(f"分析记录不存在: {analysis_id}")
        raise HTTPException(status_code=404, detail=f"分析记录不存在: {analysis_id}")
    
    # 删除关联的任务状态记录
    task_id = analysis.get("task_id")
    if task_id:
        await db.analysis_tasks.delete_one({"task_id": task_id})
        logger.info(f"已删除关联的任务状态记录: {task_id}")
    
    # 删除分析记录
    result = await db.analysis_records.delete_one({"analysis_id": analysis_id})
    
    if result.deleted_count == 0:
        logger.warning(f"删除分析记录失败: {analysis_id}")
        raise HTTPException(status_code=500, detail="删除分析记录失败")
    
    logger.info(f"已成功删除分析记录: {analysis_id}")
    
    return success_response({"message": "分析记录删除成功"})


@router.get("/history")
async def get_all_analysis_history(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页记录数"),
    status: Optional[str] = Query(None, description="状态过滤"),
    analysis_type: Optional[str] = Query(None, description="分析类型过滤"),
    db = Depends(get_database)
):
    """获取所有项目的分析历史记录"""
    logger.info(f"获取所有分析历史, 页码: {page}, 大小: {size}")
    
    # 构建查询条件
    query = {}
    if status:
        query["status"] = status
    if analysis_type:
        query["analysis_type"] = analysis_type
    
    # 计算总数
    total = await db.analysis_records.count_documents(query)
    
    # 获取分页数据
    skip = (page - 1) * size
    cursor = db.analysis_records.find(query).sort("created_at", -1).skip(skip).limit(size)
    
    records = []
    async for record in cursor:
        # 获取相关项目信息
        project_key = record.get("project_key")
        project_name = "未知项目"
        
        if project_key:
            project = await db.projects.find_one({"project_key": project_key})
            if project:
                project_name = project.get("name", "未知项目")
        
        # 将MongoDB对象转换为可序列化的字典
        record_dict = {k: v for k, v in record.items() if k != "_id"}
        
        # 格式化日期时间字段
        for date_field in ["created_at", "updated_at"]:
            if date_field in record_dict:
                record_dict[date_field] = record_dict[date_field].isoformat()
        
        # 添加项目名称
        record_dict["project_name"] = project_name
        
        # 添加到结果列表
        records.append(record_dict)
    
    return success_response({
        "records": records,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    })


@router.get("/history/{project_key}")
async def get_project_analysis_history(
    project_key: str = Path(..., description="项目标识"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页记录数"),
    status: Optional[str] = Query(None, description="状态过滤"),
    analysis_type: Optional[str] = Query(None, description="分析类型过滤"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db = Depends(get_database)
):
    """获取指定项目的分析历史记录"""
    logger.info(f"获取项目 {project_key} 的分析历史, 页码: {page}, 大小: {size}")
    
    # 检查项目是否存在
    project = await db.projects.find_one({"project_key": project_key})
    if not project:
        logger.warning(f"项目不存在: {project_key}")
        raise HTTPException(status_code=404, detail=f"项目不存在: {project_key}")
    
    # 构建查询条件
    query = {"project_key": project_key}
    if status:
        query["status"] = status
    if analysis_type:
        query["analysis_type"] = analysis_type
    
    # 添加日期范围过滤
    if start_date or end_date:
        date_query = {}
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                date_query["$gte"] = start_datetime
            except ValueError:
                logger.warning(f"无效的开始日期格式: {start_date}")
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                date_query["$lte"] = end_datetime
            except ValueError:
                logger.warning(f"无效的结束日期格式: {end_date}")
        
        if date_query:
            query["created_at"] = date_query
    
    # 计算总数
    total = await db.analysis_records.count_documents(query)
    
    # 获取分页数据
    skip = (page - 1) * size
    cursor = db.analysis_records.find(query).sort("created_at", -1).skip(skip).limit(size)
    
    records = []
    async for record in cursor:
        # 将MongoDB对象转换为可序列化的字典
        record_dict = {k: v for k, v in record.items() if k != "_id"}
        
        # 格式化日期时间字段
        for date_field in ["created_at", "updated_at"]:
            if date_field in record_dict:
                record_dict[date_field] = record_dict[date_field].isoformat()
        
        # 添加项目名称
        record_dict["project_name"] = project.get("name", "未知项目")
        
        # 添加到结果列表
        records.append(record_dict)
    
    return success_response({
        "records": records,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    })