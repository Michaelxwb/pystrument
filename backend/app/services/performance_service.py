"""
性能数据管理服务
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from app.utils.database import get_database
from app.models.performance import PerformanceRecord, PerformanceRecordCreate, FunctionCallDetail

logger = logging.getLogger(__name__)


class PerformanceService:
    """性能数据管理服务类"""
    
    def __init__(self):
        self.db = get_database()
        self.performance_collection = self.db.performance_records if self.db is not None else None
        self.function_calls_collection = self.db.function_calls if self.db is not None else None
        self.analysis_collection = self.db.ai_analysis_results if self.db is not None else None
    
    async def save_performance_record(
        self, 
        project_key: str, 
        performance_data: PerformanceRecordCreate
    ) -> PerformanceRecord:
        """保存性能记录"""
        try:
            # 创建性能记录
            record = PerformanceRecord(
                project_key=project_key,
                **performance_data.dict()
            )
            
            # 保存主记录
            await self.performance_collection.insert_one(record.to_dict())
            
            # 保存详细的函数调用记录
            if record.function_calls:
                function_call_details = []
                for i, func_call in enumerate(record.function_calls):
                    detail = FunctionCallDetail(
                        trace_id=record.trace_id,
                        call_id=func_call.call_id,
                        parent_call_id=func_call.parent_call_id,
                        function_info={
                            "name": func_call.function_name,
                            "file_path": func_call.file_path,
                            "line_number": func_call.line_number
                        },
                        execution_info={
                            "duration": func_call.duration,
                            "start_time": record.timestamp,
                            "end_time": record.timestamp
                        },
                        call_context={
                            "depth": func_call.depth,
                            "call_order": func_call.call_order,
                            "is_recursive": False
                        },
                        performance_tags=[]
                    )
                    
                    # 根据耗时添加性能标签
                    if func_call.duration > 1.0:
                        detail.performance_tags.append("slow")
                    if "sql" in func_call.function_name.lower() or "query" in func_call.function_name.lower():
                        detail.performance_tags.append("database")
                    if "cache" in func_call.function_name.lower():
                        detail.performance_tags.append("cache")
                    
                    function_call_details.append(detail.to_dict())
                
                if function_call_details:
                    await self.function_calls_collection.insert_many(function_call_details)
            
            logger.info(f"保存性能记录成功: {record.trace_id}")
            return record
            
        except Exception as e:
            logger.error(f"保存性能记录失败: {str(e)}")
            raise
    
    async def get_performance_records(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 20
    ) -> Tuple[List[PerformanceRecord], int]:
        """获取性能记录列表"""
        try:
            query = filters or {}
            
            # 计算总数
            total = await self.performance_collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * size
            cursor = self.performance_collection.find(query).skip(skip).limit(size).sort("timestamp", -1)
            
            records = []
            async for doc in cursor:
                doc.pop("_id", None)
                records.append(PerformanceRecord.from_dict(doc))
            
            return records, total
            
        except Exception as e:
            logger.error(f"获取性能记录列表失败: {str(e)}")
            raise
    
    async def get_performance_record_by_trace_id(self, trace_id: str) -> Optional[PerformanceRecord]:
        """根据trace_id获取性能记录详情"""
        try:
            doc = await self.performance_collection.find_one({"trace_id": trace_id})
            if doc:
                doc.pop("_id", None)
                return PerformanceRecord.from_dict(doc)
            return None
            
        except Exception as e:
            logger.error(f"获取性能记录详情失败: {str(e)}")
            raise
    
    async def get_performance_stats(
        self,
        project_key: str,
        start_time: datetime,
        group_by: str = "hour"
    ) -> Dict[str, Any]:
        """获取性能统计信息"""
        try:
            # 构建聚合管道
            match_stage = {
                "project_key": project_key,
                "timestamp": {"$gte": start_time}
            }
            
            # 根据分组方式确定日期格式
            if group_by == "hour":
                date_format = "%Y-%m-%d %H:00"
            else:  # day
                date_format = "%Y-%m-%d"
            
            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": date_format,
                                "date": "$timestamp"
                            }
                        },
                        "count": {"$sum": 1},
                        "avg_duration": {"$avg": "$performance_metrics.total_duration"},
                        "max_duration": {"$max": "$performance_metrics.total_duration"},
                        "min_duration": {"$min": "$performance_metrics.total_duration"},
                        "error_count": {
                            "$sum": {
                                "$cond": [
                                    {"$gte": ["$response_info.status_code", 400]},
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            # 执行聚合查询
            results = await self.performance_collection.aggregate(pipeline).to_list(None)
            
            # 格式化结果
            time_series = []
            total_requests = 0
            total_errors = 0
            avg_duration_sum = 0
            
            for result in results:
                time_series.append({
                    "time": result["_id"],
                    "requests": result["count"],
                    "avg_duration": round(result["avg_duration"], 3),
                    "max_duration": round(result["max_duration"], 3),
                    "min_duration": round(result["min_duration"], 3),
                    "error_rate": round(result["error_count"] / result["count"] * 100, 2)
                })
                total_requests += result["count"]
                total_errors += result["error_count"]
                avg_duration_sum += result["avg_duration"]
            
            # 计算整体统计
            overall_avg_duration = avg_duration_sum / len(results) if results else 0
            overall_error_rate = total_errors / total_requests * 100 if total_requests > 0 else 0
            
            return {
                "time_series": time_series,
                "summary": {
                    "total_requests": total_requests,
                    "total_errors": total_errors,
                    "overall_avg_duration": round(overall_avg_duration, 3),
                    "overall_error_rate": round(overall_error_rate, 2),
                    "period": f"{start_time.isoformat()} - {datetime.utcnow().isoformat()}"
                }
            }
            
        except Exception as e:
            logger.error(f"获取性能统计失败: {str(e)}")
            raise
    
    async def get_performance_trends(
        self,
        project_key: str,
        start_time: datetime,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """获取性能趋势数据"""
        try:
            # 根据时间范围确定分组方式
            if time_range in ["1h", "6h"]:
                group_by = "minute"
                date_format = "%Y-%m-%d %H:%M"
                interval_minutes = 10  # 10分钟间隔
            elif time_range == "24h":
                group_by = "hour"
                date_format = "%Y-%m-%d %H:00"
                interval_minutes = 60  # 1小时间隔
            else:  # 7d
                group_by = "day"
                date_format = "%Y-%m-%d"
                interval_minutes = 1440  # 1天间隔
            
            # 记录查询参数
            logger.info(f"获取性能趋势数据: project_key='{project_key}', time_range={time_range}, start_time={start_time.isoformat()}")
            
            # 获取响应时间趋势数据
            response_times = await self._get_response_time_trends(
                project_key, start_time, date_format
            )
            
            # 获取接口性能分布数据
            endpoint_stats = await self._get_endpoint_performance_stats(
                project_key, start_time
            )
            
            # 记录结果
            logger.info(f"性能趋势数据结果: response_times={len(response_times)}, endpoint_stats={len(endpoint_stats)}")
            
            # 确保返回空数组而不是None
            if response_times is None:
                response_times = []
            if endpoint_stats is None:
                endpoint_stats = []
            
            return {
                "response_times": response_times,
                "endpoint_stats": endpoint_stats,
                "time_range": time_range,
                "period": f"{start_time.isoformat()} - {datetime.utcnow().isoformat()}"
            }
            
        except Exception as e:
            logger.error(f"获取性能趋势数据失败: {str(e)}")
            # 返回空数据而不是抛出异常
            return {
                "response_times": [],
                "endpoint_stats": [],
                "time_range": time_range,
                "period": f"{start_time.isoformat()} - {datetime.utcnow().isoformat()}",
                "error": str(e)
            }
    
    async def _get_response_time_trends(
        self,
        project_key: str,
        start_time: datetime,
        date_format: str
    ) -> List[Dict[str, Any]]:
        """获取响应时间趋势数据"""
        # 构建查询条件
        match_condition = {"timestamp": {"$gte": start_time}}
        if project_key and project_key.strip():  # 检查项目密钥是否有效（非空且非空白字符）
            match_condition["project_key"] = project_key
            
        # 添加日志，记录构建的查询条件
        logger.info(f"响应时间趋势查询条件: {match_condition}")
            
        pipeline = [
            {
                "$match": match_condition
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": date_format,
                            "date": "$timestamp"
                        }
                    },
                    "avg_duration": {"$avg": "$performance_metrics.total_duration"},
                    "request_count": {"$sum": 1},
                    "max_duration": {"$max": "$performance_metrics.total_duration"},
                    "min_duration": {"$min": "$performance_metrics.total_duration"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        results = await self.performance_collection.aggregate(pipeline).to_list(None)
        
        return [
            {
                "time": result["_id"],
                "avg_duration": round(result["avg_duration"], 3),
                "request_count": result["request_count"],
                "max_duration": round(result["max_duration"], 3),
                "min_duration": round(result["min_duration"], 3)
            }
            for result in results
        ]
    
    async def _get_endpoint_performance_stats(
        self,
        project_key: str,
        start_time: datetime,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取接口性能分布数据"""
        # 构建查询条件
        match_condition = {"timestamp": {"$gte": start_time}}
        if project_key and project_key.strip():  # 检查项目密钥是否有效（非空且非空白字符）
            match_condition["project_key"] = project_key
            
        # 添加日志，记录构建的查询条件
        logger.info(f"接口性能分布查询条件: {match_condition}")
            
        pipeline = [
            {
                "$match": match_condition
            },
            {
                "$group": {
                    "_id": "$request_info.path",
                    "avg_duration": {"$avg": "$performance_metrics.total_duration"},
                    "request_count": {"$sum": 1},
                    "total_duration": {"$sum": "$performance_metrics.total_duration"}
                }
            },
            {"$sort": {"total_duration": -1}},
            {"$limit": limit}
        ]
        
        results = await self.performance_collection.aggregate(pipeline).to_list(None)
        
        return [
            {
                "path": result["_id"],
                "avg_duration": round(result["avg_duration"], 3),
                "request_count": result["request_count"],
                "total_duration": round(result["total_duration"], 3)
            }
            for result in results
        ]

    async def get_slow_functions(
        self,
        project_key: str,
        min_duration: float = 0.1,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取慢函数统计"""
        try:
            # 首先获取项目的trace_id列表
            trace_ids = await self.performance_collection.find(
                {"project_key": project_key},
                {"trace_id": 1}
            ).to_list(None)
            
            trace_id_list = [doc["trace_id"] for doc in trace_ids]
            
            if not trace_id_list:
                return []
            
            # 聚合查询慢函数
            pipeline = [
                {
                    "$match": {
                        "trace_id": {"$in": trace_id_list},
                        "execution_info.duration": {"$gte": min_duration}
                    }
                },
                {
                    "$group": {
                        "_id": "$function_info.name",
                        "total_calls": {"$sum": 1},
                        "total_duration": {"$sum": "$execution_info.duration"},
                        "avg_duration": {"$avg": "$execution_info.duration"},
                        "max_duration": {"$max": "$execution_info.duration"},
                        "file_path": {"$first": "$function_info.file_path"}
                    }
                },
                {
                    "$sort": {"total_duration": -1}
                },
                {
                    "$limit": limit
                }
            ]
            
            results = await self.function_calls_collection.aggregate(pipeline).to_list(None)
            
            slow_functions = []
            for result in results:
                slow_functions.append({
                    "function_name": result["_id"],
                    "file_path": result["file_path"],
                    "total_calls": result["total_calls"],
                    "total_duration": round(result["total_duration"], 3),
                    "avg_duration": round(result["avg_duration"], 3),
                    "max_duration": round(result["max_duration"], 3),
                    "performance_impact": round(result["total_duration"] / result["total_calls"], 3)
                })
            
            return slow_functions
            
        except Exception as e:
            logger.error(f"获取慢函数统计失败: {str(e)}")
            raise
    
    async def get_function_call_tree(self, trace_id: str) -> Dict[str, Any]:
        """获取函数调用树"""
        try:
            # 首先从性能记录中获取函数调用数据
            record = await self.get_performance_record_by_trace_id(trace_id)
            if not record or not record.function_calls:
                logger.warning(f"无法获取函数调用数据: {trace_id}")
                return {
                    "trace_id": trace_id,
                    "call_tree": [],
                    "total_functions": 0
                }
            
            # 使用记录中的函数调用数据
            function_calls = record.function_calls
            
            # 构建调用树
            call_map = {}
            root_calls = []
            
            # 首先创建所有节点
            for call in function_calls:
                call_map[call.call_id] = {
                    "call_id": call.call_id,
                    "function_name": call.function_name,
                    "duration": call.duration,
                    "file_path": call.file_path,
                    "line_number": call.line_number,
                    "depth": call.depth,
                    "call_order": call.call_order,
                    "children": []
                }
            
            # 建立父子关系
            for call in function_calls:
                if call.parent_call_id and call.parent_call_id in call_map:
                    parent = call_map[call.parent_call_id]
                    parent["children"].append(call_map[call.call_id])
                else:
                    root_calls.append(call_map[call.call_id])
            
            # 如果没有找到根调用，则按深度和调用顺序排序
            if not root_calls and function_calls:
                function_calls_sorted = sorted(function_calls, key=lambda x: (x.depth, x.call_order))
                for call in function_calls_sorted:
                    if call.depth == 0 or not any(c.call_id == call.parent_call_id for c in function_calls):
                        root_calls.append(call_map[call.call_id])
            
            logger.info(f"成功构建函数调用树: {trace_id}, 函数数量: {len(function_calls)}, 根调用数量: {len(root_calls)}")
            
            return {
                "trace_id": trace_id,
                "call_tree": root_calls,
                "total_functions": len(function_calls)
            }
            
        except Exception as e:
            logger.error(f"获取函数调用树失败: {str(e)}")
            # 返回空结果而不是抛出异常
            return {
                "trace_id": trace_id,
                "call_tree": [],
                "total_functions": 0,
                "error": str(e)
            }
    
    async def get_total_records_count(self) -> int:
        """获取性能记录总数"""
        try:
            return await self.performance_collection.count_documents({})
        except Exception as e:
            logger.error(f"获取性能记录总数失败: {str(e)}")
            return 0
    
    async def get_analysis_count_since(self, start_time: datetime) -> int:
        """获取指定时间之后的分析数量"""
        try:
            return await self.analysis_collection.count_documents({
                "created_at": {"$gte": start_time}
            })
        except Exception as e:
            logger.error(f"获取分析数量失败: {str(e)}")
            return 0
    
    async def get_average_response_time(self) -> float:
        """获取所有项目的平均响应时间"""
        try:
            pipeline = [
                {"$group": {
                    "_id": None,
                    "avg_duration": {"$avg": "$performance_metrics.total_duration"}
                }}
            ]
            
            result = await self.performance_collection.aggregate(pipeline).to_list(1)
            if result and len(result) > 0:
                avg_duration = result[0].get("avg_duration", 0)
                return round(avg_duration * 1000, 3)  # 转换为毫秒并保留3位小数
            return 0
        except Exception as e:
            logger.error(f"获取平均响应时间失败: {str(e)}")
            return 0
    
    async def get_record_count_by_project(self, project_key: str) -> int:
        """获取指定项目的记录数量"""
        try:
            return await self.performance_collection.count_documents({
                "project_key": project_key
            })
        except Exception as e:
            logger.error(f"获取项目记录数量失败: {str(e)}")
            return 0
    
    async def get_recent_analysis(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近的分析结果"""
        try:
            cursor = self.analysis_collection.find().sort("created_at", -1).limit(limit)
            
            analysis_results = []
            async for doc in cursor:
                doc.pop("_id", None)
                
                # 获取项目名称
                project_key = doc.get("project_key")
                project_name = project_key
                try:
                    project_service = ProjectService()
                    project = await project_service.get_project_by_key(project_key)
                    if project:
                        project_name = project.name
                except Exception:
                    pass
                
                analysis_results.append({
                    "projectName": project_name,
                    "type": doc.get("analysis_type", "AI分析"),
                    "status": doc.get("status", "completed"),
                    "createdAt": doc.get("created_at").isoformat() if doc.get("created_at") else None
                })
            
            return analysis_results
        except Exception as e:
            logger.error(f"获取最近分析结果失败: {str(e)}")
            return []
