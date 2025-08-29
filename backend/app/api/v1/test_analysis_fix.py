"""
修复AI分析模块中Celery任务与API之间的analysis_id不匹配问题
"""
from fastapi import APIRouter, HTTPException, Path, Depends, Body, Query
from typing import Dict, Any, Optional, List
import logging
import uuid
from datetime import datetime, timedelta

from app.utils.response import success_response, error_response
from app.utils.database import get_database
from app.models.analysis import AnalysisRequest, TaskStatus, AnalysisRecord
from app.tasks.ai_analysis import analyze_performance_task
from app.tasks.ai_analysis_fix import analyze_performance_fixed_task
from app.services.ai_config import ai_config_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/fixed-analyze/{performance_record_id}")
async def analyze_performance_fixed(
    performance_record_id: str = Path(..., description="性能记录ID"),
    request: AnalysisRequest = Body(...),
    db = Depends(get_database)
):
    """
    修复版本：触发对单个性能记录的AI分析
    """
    logger.info(f"收到性能记录分析请求(修复版): {performance_record_id}, 服务: {request.ai_service}")
    
    # 检查性能记录是否存在
    performance_record = await db.performance_records.find_one({"trace_id": performance_record_id})
    if not performance_record:
        logger.warning(f"性能记录不存在: {performance_record_id}")
        raise HTTPException(status_code=404, detail=f"性能记录不存在: {performance_record_id}")
    
    # 处理AI服务名称
    ai_service_name = request.ai_service
    if ai_service_name == "default":
        # 使用配置管理器中的默认服务
        ai_service_name = ai_config_manager.default_service
        logger.info(f"使用默认AI服务: {ai_service_name}")
    
    # 创建固定的analysis_id
    analysis_id = f"analysis_{performance_record_id}_{int(datetime.utcnow().timestamp())}"
    
    # 创建分析记录
    analysis_record = {
        "analysis_id": analysis_id,
        "performance_record_id": performance_record_id,
        "project_key": performance_record.get("project_key"),
        "ai_service": ai_service_name,
        "status": "PENDING",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "results": None,
        "priority": request.priority.value
    }
    
    await db.ai_analysis_results.insert_one(analysis_record)
    
    logger.info(f"已创建分析任务(修复版): {task_id}, 分析ID: {analysis_id}")
    
    return success_response({
        "analysis_id": analysis_id,
        "task_id": task_id,
        "status": "PENDING",
        "estimated_completion": (datetime.utcnow() + timedelta(minutes=2)).isoformat()
    })


@router.get("/fixed-result/{analysis_id}")
async def get_fixed_analysis_result(
    analysis_id: str = Path(..., description="分析ID"),
    db = Depends(get_database)
):
    """
    获取修复版分析结果
    """
    logger.info(f"获取修复版分析结果: {analysis_id}")
    
    analysis = await db.ai_analysis_results.find_one({"analysis_id": analysis_id})
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