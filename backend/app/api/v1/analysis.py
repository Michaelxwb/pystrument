"""
AI分析相关API路由
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from app.core.response import ApiResponse, success_response, error_response
from app.services.database import db_manager
from app.tasks.ai_analysis import (
    analyze_performance_task,
    batch_analyze_performance_task,
    generate_performance_report_task,
    celery_app
)
from app.models.analysis import AnalysisRecord, AnalysisRequest, BatchAnalysisRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/analysis", tags=["AI分析"])


@router.post("/analyze/{performance_record_id}")
async def trigger_analysis(
    performance_record_id: str,
    request: AnalysisRequest
) -> ApiResponse:
    """
    触发单个性能记录的AI分析
    
    Args:
        performance_record_id: 性能记录ID
        request: 分析请求参数
    """
    try:
        # 检查性能记录是否存在
        performance_record = await db_manager.get_performance_record(performance_record_id)
        if not performance_record:
            return error_response(20001, "性能记录不存在", {})
        
        # 检查是否已经有进行中的分析
        existing_analysis = await db_manager.get_analysis_by_performance_id(
            performance_record_id, status="processing"
        )
        if existing_analysis:
            return error_response(20006, "该记录的分析正在进行中", {
                "analysis_id": existing_analysis.get("id"),
                "task_id": existing_analysis.get("task_id")
            })
        
        # 触发异步分析任务
        task = analyze_performance_task.delay(
            performance_record_id=performance_record_id,
            ai_service=request.ai_service,
            priority=request.priority
        )
        
        # 创建分析记录
        analysis_record = AnalysisRecord(
            id=f"analysis_{performance_record_id}_{int(datetime.utcnow().timestamp())}",
            performance_record_id=performance_record_id,
            project_key=performance_record.get("project_key"),
            analysis_type="ai_analysis",
            ai_service=request.ai_service or "default",
            results={},
            task_id=task.id,
            status="processing",
            created_at=datetime.utcnow()
        )
        
        await db_manager.save_analysis_record(analysis_record)
        
        return success_response({
            "analysis_id": analysis_record.id,
            "task_id": task.id,
            "status": "processing",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=2)).isoformat()
        })
        
    except Exception as e:
        logger.error(f"触发分析失败: {str(e)}")
        return error_response(10000, f"触发分析失败: {str(e)}", {})


@router.post("/batch-analyze")
async def trigger_batch_analysis(request: BatchAnalysisRequest) -> ApiResponse:
    """
    触发批量性能分析
    
    Args:
        request: 批量分析请求参数
    """
    try:
        # 检查性能记录是否存在
        valid_records = []
        for record_id in request.performance_record_ids:
            record = await db_manager.get_performance_record(record_id)
            if record:
                valid_records.append(record_id)
        
        if not valid_records:
            return error_response(20001, "没有找到有效的性能记录", {})
        
        # 触发批量分析任务
        task = batch_analyze_performance_task.delay(
            performance_record_ids=valid_records,
            ai_service=request.ai_service,
            priority=request.priority
        )
        
        return success_response({
            "batch_task_id": task.id,
            "total_records": len(valid_records),
            "invalid_records": len(request.performance_record_ids) - len(valid_records),
            "status": "processing"
        })
        
    except Exception as e:
        logger.error(f"触发批量分析失败: {str(e)}")
        return error_response(10000, f"触发批量分析失败: {str(e)}", {})


@router.get("/result/{analysis_id}")
async def get_analysis_result(analysis_id: str) -> ApiResponse:
    """
    获取分析结果
    
    Args:
        analysis_id: 分析记录ID
    """
    try:
        analysis_record = await db_manager.get_analysis_record(analysis_id)
        if not analysis_record:
            return error_response(20001, "分析记录不存在", {})
        
        return success_response(analysis_record)
        
    except Exception as e:
        logger.error(f"获取分析结果失败: {str(e)}")
        return error_response(10000, f"获取分析结果失败: {str(e)}", {})


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str) -> ApiResponse:
    """
    获取任务状态
    
    Args:
        task_id: Celery任务ID
    """
    try:
        # 获取任务状态
        task_result = celery_app.AsyncResult(task_id)
        
        status_info = {
            "task_id": task_id,
            "status": task_result.status,
            "result": None,
            "traceback": None,
            "meta": None
        }
        
        if task_result.ready():
            if task_result.successful():
                status_info["result"] = task_result.result
            else:
                status_info["traceback"] = task_result.traceback
        else:
            # 获取任务进度信息
            status_info["meta"] = task_result.info
        
        return success_response(status_info)
        
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        return error_response(10000, f"获取任务状态失败: {str(e)}", {})


@router.get("/history/{project_key}")
async def get_analysis_history(
    project_key: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    analysis_type: Optional[str] = Query(None, description="分析类型筛选"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期")
) -> ApiResponse:
    """
    获取项目的分析历史
    
    Args:
        project_key: 项目键
        page: 页码
        size: 每页数量
        status: 状态筛选
        analysis_type: 分析类型筛选
        start_date: 开始日期
        end_date: 结束日期
    """
    try:
        # 构建查询条件
        query_params = {
            "project_key": project_key,
            "page": page,
            "size": size
        }
        
        if status:
            query_params["status"] = status
        if analysis_type:
            query_params["analysis_type"] = analysis_type
        if start_date:
            query_params["start_date"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if end_date:
            query_params["end_date"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # 查询分析历史
        result = await db_manager.get_analysis_history(**query_params)
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f"获取分析历史失败: {str(e)}")
        return error_response(10000, f"获取分析历史失败: {str(e)}", {})


@router.get("/summary/{project_key}")
async def get_analysis_summary(
    project_key: str,
    days: int = Query(30, ge=1, le=365, description="统计天数")
) -> ApiResponse:
    """
    获取项目分析汇总
    
    Args:
        project_key: 项目键
        days: 统计天数
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取汇总数据
        summary = await db_manager.get_analysis_summary(project_key, start_date)
        
        return success_response(summary)
        
    except Exception as e:
        logger.error(f"获取分析汇总失败: {str(e)}")
        return error_response(10000, f"获取分析汇总失败: {str(e)}", {})


@router.post("/report/{project_key}")
async def generate_performance_report(
    project_key: str,
    start_date: str,
    end_date: str,
    report_type: str = Query("summary", description="报告类型: summary, detailed, trend")
) -> ApiResponse:
    """
    生成性能分析报告
    
    Args:
        project_key: 项目键
        start_date: 开始日期
        end_date: 结束日期
        report_type: 报告类型
    """
    try:
        # 触发报告生成任务
        task = generate_performance_report_task.delay(
            project_key=project_key,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type
        )
        
        return success_response({
            "task_id": task.id,
            "status": "processing",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        })
        
    except Exception as e:
        logger.error(f"生成报告失败: {str(e)}")
        return error_response(10000, f"生成报告失败: {str(e)}", {})


@router.get("/report-status/{task_id}")
async def get_report_status(task_id: str) -> ApiResponse:
    """
    获取报告生成状态
    
    Args:
        task_id: 任务ID
    """
    try:
        # 获取任务状态
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.ready():
            if task_result.successful():
                result = task_result.result
                return success_response({
                    "status": "completed",
                    "report_id": result.get("report_id"),
                    "summary": result.get("summary")
                })
            else:
                return error_response(10000, "报告生成失败", {
                    "error": str(task_result.info)
                })
        else:
            return success_response({
                "status": "processing",
                "progress": task_result.info.get("progress", 0) if task_result.info else 0
            })
        
    except Exception as e:
        logger.error(f"获取报告状态失败: {str(e)}")
        return error_response(10000, f"获取报告状态失败: {str(e)}", {})


@router.delete("/cleanup/{project_key}")
async def cleanup_analysis_data(
    project_key: str,
    days: int = Query(30, ge=1, description="保留天数")
) -> ApiResponse:
    """
    清理项目的分析数据
    
    Args:
        project_key: 项目键
        days: 保留天数，超过此天数的数据将被删除
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 删除旧的分析记录
        result = await db_manager.cleanup_project_analysis_records(project_key, cutoff_date)
        
        return success_response({
            "deleted_count": result.get("deleted_count", 0),
            "cutoff_date": cutoff_date.isoformat()
        })
        
    except Exception as e:
        logger.error(f"清理分析数据失败: {str(e)}")
        return error_response(10000, f"清理分析数据失败: {str(e)}", {})


@router.get("/config/ai-services")
async def get_ai_services() -> ApiResponse:
    """
    获取可用的AI服务列表
    """
    try:
        from app.services.ai_config import ai_config_manager
        
        services = ai_config_manager.get_all_services()
        
        # 过滤敏感信息
        public_services = []
        for service_name, config in services.items():
            if config.enabled:
                public_services.append({
                    "name": service_name,
                    "provider": config.provider.value,
                    "description": config.description,
                    "capabilities": config.capabilities
                })
        
        return success_response(public_services)
        
    except Exception as e:
        logger.error(f"获取AI服务列表失败: {str(e)}")
        return error_response(10000, f"获取AI服务列表失败: {str(e)}", {})