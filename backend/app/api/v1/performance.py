"""
性能数据收集和查询API路由
"""
from fastapi import APIRouter, HTTPException, Query, Header, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import json

from app.utils.response import success_response, error_response, ErrorCode
from app.models.performance import PerformanceRecord, PerformanceRecordCreate
from app.services.performance_service import PerformanceService
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("/collect", summary="性能数据上报")
async def collect_performance_data(
    performance_data: PerformanceRecordCreate,
    x_project_key: str = Header(..., alias="X-Project-Key", description="项目密钥")
):
    """接收第三方应用上报的性能数据"""
    try:
        # 验证项目密钥
        project_service = ProjectService()
        project = await project_service.get_project_by_key(x_project_key)
        if not project:
            return error_response(
                ErrorCode.INVALID_PROJECT_KEY,
                "无效的项目密钥"
            )
        
        # 检查项目是否启用监控
        if not project.config.get("enabled", True):
            return error_response(
                ErrorCode.PERMISSION_ERROR,
                "项目监控已禁用"
            )
        
        # 保存性能数据
        performance_service = PerformanceService()
        record = await performance_service.save_performance_record(
            x_project_key, 
            performance_data
        )
        
        # 更新项目最后活跃时间
        await project_service.update_last_activity(x_project_key)
        
        return success_response(
            data={
                "trace_id": record.trace_id,
                "recorded_at": record.created_at.isoformat()
            },
            msg="性能数据收集成功"
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"性能数据收集失败: {str(e)}"
        )


@router.get("/records", summary="查询性能记录")
async def get_performance_records(
    project_key: str = Query(..., description="项目密钥"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    path: Optional[str] = Query(None, description="请求路径"),
    method: Optional[str] = Query(None, description="HTTP方法"),
    min_duration: Optional[float] = Query(None, description="最小耗时（秒）"),
    max_duration: Optional[float] = Query(None, description="最大耗时（秒）"),
    status_code: Optional[int] = Query(None, description="HTTP状态码")
):
    """查询性能记录列表"""
    try:
        # 验证项目
        project_service = ProjectService()
        project = await project_service.get_project_by_key(project_key)
        if not project:
            return error_response(
                ErrorCode.PROJECT_NOT_FOUND,
                "项目不存在"
            )
        
        # 构建查询条件
        filters = {"project_key": project_key}
        
        if start_time or end_time:
            time_filter = {}
            if start_time:
                time_filter["$gte"] = start_time
            if end_time:
                time_filter["$lte"] = end_time
            filters["timestamp"] = time_filter
        
        if path:
            filters["request_info.path"] = {"$regex": path, "$options": "i"}
        
        if method:
            filters["request_info.method"] = method
        
        if status_code:
            filters["response_info.status_code"] = status_code
        
        if min_duration or max_duration:
            duration_filter = {}
            if min_duration:
                duration_filter["$gte"] = min_duration
            if max_duration:
                duration_filter["$lte"] = max_duration
            filters["performance_metrics.total_duration"] = duration_filter
        
        # 查询数据
        performance_service = PerformanceService()
        records, total = await performance_service.get_performance_records(
            filters=filters,
            page=page,
            size=size
        )
        
        return success_response(
            data={
                "records": [
                    {
                        "trace_id": record.trace_id,
                        "request_path": record.request_info.get("path"),
                        "request_method": record.request_info.get("method"),
                        "duration": record.performance_metrics.get("total_duration"),
                        "cpu_time": record.performance_metrics.get("cpu_time"),
                        "memory_peak": record.performance_metrics.get("memory_usage", {}).get("peak_memory"),
                        "status_code": record.response_info.get("status_code"),
                        "timestamp": record.timestamp.isoformat(),
                        "function_call_count": len(record.function_calls) if record.function_calls else 0
                    }
                    for record in records
                ],
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size
            }
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"查询性能记录失败: {str(e)}"
        )


@router.get("/records/{trace_id}", summary="获取性能记录详情")
async def get_performance_record_detail(trace_id: str):
    """获取指定trace_id的性能记录详情"""
    try:
        performance_service = PerformanceService()
        record = await performance_service.get_performance_record_by_trace_id(trace_id)
        
        if not record:
            return error_response(
                ErrorCode.PERFORMANCE_DATA_INVALID,
                "性能记录不存在"
            )
        
        return success_response(
            data={
                "trace_id": record.trace_id,
                "project_key": record.project_key,
                "request_info": record.request_info,
                "response_info": record.response_info,
                "performance_metrics": record.performance_metrics,
                "function_calls": record.function_calls,
                "version_info": record.version_info,
                "environment": record.environment,
                "timestamp": record.timestamp.isoformat(),
                "created_at": record.created_at.isoformat()
            }
        )
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取性能记录详情失败: {str(e)}"
        )


@router.get("/stats/{project_key}", summary="获取性能统计信息")
async def get_performance_stats(
    project_key: str,
    period: str = Query("7d", description="统计周期: 1d/7d/30d"),
    group_by: str = Query("hour", description="分组方式: hour/day")
):
    """获取项目性能统计信息"""
    try:
        # 验证项目
        project_service = ProjectService()
        project = await project_service.get_project_by_key(project_key)
        if not project:
            return error_response(
                ErrorCode.PROJECT_NOT_FOUND,
                "项目不存在"
            )
        
        # 计算时间范围
        period_map = {
            "1d": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        
        if period not in period_map:
            return error_response(
                ErrorCode.PARAMETER_ERROR,
                "无效的统计周期"
            )
        
        start_time = datetime.utcnow() - period_map[period]
        
        # 获取统计数据
        performance_service = PerformanceService()
        stats = await performance_service.get_performance_stats(
            project_key=project_key,
            start_time=start_time,
            group_by=group_by
        )
        
        return success_response(data=stats)
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取性能统计失败: {str(e)}"
        )


@router.get("/trends/{project_key}", summary="获取性能趋势数据")
async def get_performance_trends(
    project_key: str,
    time_range: str = Query("24h", description="时间范围: 1h/6h/24h/7d")
):
    """获取项目性能趋势数据，用于图表展示"""
    try:
        # 验证项目
        project_service = ProjectService()
        project = await project_service.get_project_by_key(project_key)
        if not project:
            return error_response(
                ErrorCode.PROJECT_NOT_FOUND,
                "项目不存在"
            )
        
        # 计算时间范围
        time_range_map = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7)
        }
        
        if time_range not in time_range_map:
            return error_response(
                ErrorCode.PARAMETER_ERROR,
                "无效的时间范围"
            )
        
        start_time = datetime.utcnow() - time_range_map[time_range]
        
        # 获取趋势数据
        performance_service = PerformanceService()
        trends = await performance_service.get_performance_trends(
            project_key=project_key,
            start_time=start_time,
            time_range=time_range
        )
        
        return success_response(data=trends)
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取性能趋势失败: {str(e)}"
        )


@router.get("/slow-functions/{project_key}", summary="获取慢函数统计")
async def get_slow_functions(
    project_key: str,
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    min_duration: float = Query(0.1, description="最小耗时阈值（秒）")
):
    """获取项目中的慢函数统计"""
    try:
        # 验证项目
        project_service = ProjectService()
        project = await project_service.get_project_by_key(project_key)
        if not project:
            return error_response(
                ErrorCode.PROJECT_NOT_FOUND,
                "项目不存在"
            )
        
        # 获取慢函数统计
        performance_service = PerformanceService()
        slow_functions = await performance_service.get_slow_functions(
            project_key=project_key,
            min_duration=min_duration,
            limit=limit
        )
        
        return success_response(data={"slow_functions": slow_functions})
        
    except Exception as e:
        return error_response(
            ErrorCode.SYSTEM_ERROR,
            f"获取慢函数统计失败: {str(e)}"
        )