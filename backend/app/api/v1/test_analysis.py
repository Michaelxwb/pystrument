"""
测试AI分析功能
"""
from fastapi import APIRouter, HTTPException, Path, Depends
import logging
from datetime import datetime

from app.utils.response import success_response, error_response
from app.utils.database import get_database
from app.services.ai_analyzer import performance_analyzer
from app.tasks.ai_analysis import analyze_performance_task

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/test-analysis-integration/{performance_record_id}")
async def test_analysis_integration(
    performance_record_id: str = Path(..., description="性能记录ID"),
    db = Depends(get_database)
):
    """
    测试AI分析集成
    """
    try:
        # 检查性能记录是否存在
        performance_record = await db.performance_records.find_one({"trace_id": performance_record_id})
        if not performance_record:
            raise HTTPException(status_code=404, detail=f"性能记录不存在: {performance_record_id}")
        
        # 获取现有的分析结果
        analysis_id = f"analysis_{performance_record_id}_{int(datetime.utcnow().timestamp())}"
        existing_analysis = await db.ai_analysis_results.find_one({"performance_record_id": performance_record_id})
        
        analysis_detail = None
        if existing_analysis:
            analysis_detail = {
                "analysis_id": existing_analysis.get("analysis_id"),
                "status": existing_analysis.get("status"),
                "ai_service": existing_analysis.get("ai_service"),
                "results": existing_analysis.get("results")
            }
        
        # 获取配置的AI服务
        from app.services.ai_config import ai_config_manager
        ai_services = ai_config_manager.get_enabled_services()
        available_services = [name for name, service in ai_services.items()]
        
        # 检查Celery任务状态
        task_status = None
        if existing_analysis and existing_analysis.get("task_id"):
            # 通过Celery后端获取任务状态
            from app.tasks.ai_analysis import celery_app
            task = celery_app.AsyncResult(existing_analysis.get("task_id"))
            if task:
                task_status = {
                    "task_id": existing_analysis.get("task_id"),
                    "status": task.state,
                    "progress": getattr(task.info, 'progress', 0) if hasattr(task, 'info') else 0,
                    "created_at": existing_analysis.get("created_at")
                }
        
        return success_response({
            "message": "AI分析集成测试",
            "performance_record_id": performance_record_id,
            "existing_analysis": analysis_detail,
            "available_ai_services": available_services,
            "task_status": task_status,
            "project_key": performance_record.get("project_key"),
            "timestamp": performance_record.get("timestamp")
        })
        
    except Exception as e:
        logger.error(f"测试AI分析集成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")

@router.post("/trigger-test-analysis/{performance_record_id}")
async def trigger_test_analysis(
    performance_record_id: str = Path(..., description="性能记录ID"),
    db = Depends(get_database)
):
    """
    触发测试分析
    """
    try:
        # 检查性能记录是否存在
        performance_record = await db.performance_records.find_one({"trace_id": performance_record_id})
        if not performance_record:
            raise HTTPException(status_code=404, detail=f"性能记录不存在: {performance_record_id}")
        
        # 使用默认AI服务
        from app.services.ai_config import ai_config_manager
        ai_service = ai_config_manager.default_service
        
        # 调用Celery任务
        celery_task = analyze_performance_task.delay(
            performance_record_id,
            ai_service,
            "normal"
        )
        
        return success_response({
            "message": "分析任务已触发",
            "task_id": celery_task.id,
            "ai_service": ai_service
        })
        
    except Exception as e:
        logger.error(f"触发测试分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"触发测试失败: {str(e)}")