"""
AI分析相关API路由
"""
from fastapi import APIRouter
import logging

from app.utils.response import success_response, error_response

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
            "/task-status/{task_id}"
        ]
    })