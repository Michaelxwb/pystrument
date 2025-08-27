"""
仪表盘API路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.utils.response import success_response, error_response, ErrorCode
from app.services.project_service import ProjectService
from app.services.performance_service import PerformanceService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard/stats", summary="获取仪表盘统计数据")
async def get_dashboard_stats():
    """获取仪表盘统计数据"""
    try:
        project_service = ProjectService()
        performance_service = PerformanceService()
        
        # 获取项目总数
        projects, total_projects = await project_service.get_projects(page=1, size=1)
        
        # 获取性能记录总数
        total_records = await performance_service.get_total_records_count()
        
        # 获取今日分析数量
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_analysis = await performance_service.get_analysis_count_since(today_start)
        
        # 获取平均响应时间
        avg_response_time = await performance_service.get_average_response_time()
        
        return success_response(
            data={
                "total_projects": total_projects,
                "total_records": total_records,
                "today_analysis": today_analysis,
                "avg_response_time": round(avg_response_time, 3),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取仪表盘统计数据失败: {str(e)}"
        )


@router.get("/dashboard/recent-projects", summary="获取最近活跃项目")
async def get_recent_projects(limit: int = 5):
    """获取最近活跃的项目"""
    try:
        project_service = ProjectService()
        performance_service = PerformanceService()
        
        # 获取最近活跃的项目
        projects, _ = await project_service.get_projects(page=1, size=limit)
        
        # 获取每个项目的记录数
        result = []
        for project in projects:
            record_count = await performance_service.get_record_count_by_project(project.project_key)
            result.append({
                "key": project.project_key,
                "name": project.name,
                "status": project.status,
                "recordCount": record_count
            })
        
        return success_response(data=result)
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取最近活跃项目失败: {str(e)}"
        )


@router.get("/dashboard/recent-analysis", summary="获取最近分析结果")
async def get_recent_analysis(limit: int = 5):
    """获取最近的分析结果"""
    try:
        performance_service = PerformanceService()
        
        # 获取最近的分析结果
        analysis_results = await performance_service.get_recent_analysis(limit)
        
        return success_response(data=analysis_results)
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取最近分析结果失败: {str(e)}"
        )


@router.get("/dashboard/system-info", summary="获取系统信息")
async def get_system_info():
    """获取系统信息"""
    try:
        project_service = ProjectService()
        
        # 获取系统运行信息
        system_start_time = datetime.utcnow() - timedelta(days=2, hours=14)  # 示例数据，实际应从系统配置中获取
        
        # 检查数据库和Redis状态
        db_status = "正常"
        redis_status = "正常"
        
        # 获取平台版本
        version = "v1.0.0"  # 示例数据，实际应从配置中获取
        
        return success_response(
            data={
                "version": version,
                "uptime": format_uptime(system_start_time),
                "db_status": db_status,
                "redis_status": redis_status
            }
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取系统信息失败: {str(e)}"
        )


@router.get("/dashboard/performance-trends", summary="获取性能趋势数据")
async def get_performance_trends(time_range: str = "7d"):
    """获取性能趋势数据"""
    try:
        performance_service = PerformanceService()
        
        # 计算开始时间
        now = datetime.utcnow()
        if time_range == "1h":
            start_time = now - timedelta(hours=1)
        elif time_range == "6h":
            start_time = now - timedelta(hours=6)
        elif time_range == "24h":
            start_time = now - timedelta(hours=24)
        elif time_range == "7d":
            start_time = now - timedelta(days=7)
        elif time_range == "30d":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(days=7)  # 默认7天
        
        # 日志记录请求信息
        logger.info(f"获取性能趋势数据: time_range={time_range}, start_time={start_time.isoformat()}")
        
        # 获取性能趋势数据
        trends_data = await performance_service.get_performance_trends(
            project_key="",  # 空字符串表示获取所有项目的趋势数据
            start_time=start_time,
            time_range=time_range
        )
        
        # 日志记录结果
        response_times_count = len(trends_data.get('response_times', []))
        endpoint_stats_count = len(trends_data.get('endpoint_stats', []))
        logger.info(f"性能趋势数据结果: response_times={response_times_count}, endpoint_stats={endpoint_stats_count}")
        
        # 确保有空数组而不是None
        if 'response_times' not in trends_data or trends_data['response_times'] is None:
            trends_data['response_times'] = []
        if 'endpoint_stats' not in trends_data or trends_data['endpoint_stats'] is None:
            trends_data['endpoint_stats'] = []
        
        return success_response(data=trends_data)
        
    except Exception as e:
        logger.error(f"获取性能趋势数据失败: {str(e)}")
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取性能趋势数据失败: {str(e)}"
        )


def format_uptime(start_time: datetime) -> str:
    """格式化系统运行时间"""
    delta = datetime.utcnow() - start_time
    days = delta.days
    hours = delta.seconds // 3600
    
    return f"{days}天 {hours}小时"