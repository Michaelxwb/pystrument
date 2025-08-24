"""
性能数据管理服务
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

from app.config.database import get_database
from app.models.performance import PerformanceRecord, PerformanceRecordCreate, FunctionCallDetail

logger = logging.getLogger(__name__)


class PerformanceService:
    """性能数据管理服务类"""
    
    def __init__(self):
        self.db = get_database()
        self.performance_collection = self.db.performance_records if self.db else None
        self.function_calls_collection = self.db.function_calls if self.db else None
    
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
            # 获取所有函数调用记录
            cursor = self.function_calls_collection.find({"trace_id": trace_id}).sort("call_context.call_order", 1)
            function_calls = await cursor.to_list(None)
            
            if not function_calls:
                return {}
            
            # 构建调用树
            call_map = {}
            root_calls = []
            
            for call in function_calls:
                call_id = call["call_id"]
                call_map[call_id] = {
                    "call_id": call_id,
                    "function_name": call["function_info"]["name"],
                    "duration": call["execution_info"]["duration"],
                    "file_path": call["function_info"]["file_path"],
                    "children": []
                }
                
                parent_id = call.get("parent_call_id")
                if parent_id:
                    if parent_id in call_map:
                        call_map[parent_id]["children"].append(call_map[call_id])
                else:
                    root_calls.append(call_map[call_id])
            
            return {
                "trace_id": trace_id,
                "call_tree": root_calls,
                "total_functions": len(function_calls)
            }
            
        except Exception as e:
            logger.error(f"获取函数调用树失败: {str(e)}")
            raise