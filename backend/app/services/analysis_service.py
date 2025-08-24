"""
AI分析服务
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from app.config.database import get_database
from app.models.analysis import AnalysisResult, AIService, AnalysisInput, AnalysisResults

logger = logging.getLogger(__name__)


class AnalysisService:
    """AI分析服务类"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.ai_analysis_results if self.db else None
    
    async def create_analysis_task(
        self,
        analysis_id: str,
        project_key: str,
        trace_id: str,
        analysis_type: str = "manual",
        ai_service: str = "openai"
    ) -> AnalysisResult:
        """创建AI分析任务"""
        try:
            # 创建AI服务信息
            ai_service_info = AIService(
                provider=ai_service,
                model="gpt-4" if ai_service == "openai" else "custom",
                version="1.0"
            )
            
            # 创建分析结果
            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                project_key=project_key,
                trace_id=trace_id,
                analysis_type=analysis_type,
                ai_service=ai_service_info,
                status="pending"
            )
            
            # 保存到数据库
            await self.collection.insert_one(analysis_result.to_dict())
            
            logger.info(f"创建AI分析任务成功: {analysis_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"创建AI分析任务失败: {str(e)}")
            raise
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[AnalysisResult]:
        """根据分析ID获取分析结果"""
        try:
            doc = await self.collection.find_one({"analysis_id": analysis_id})
            if doc:
                doc.pop("_id", None)
                return AnalysisResult.from_dict(doc)
            return None
            
        except Exception as e:
            logger.error(f"获取分析结果失败: {str(e)}")
            raise
    
    async def get_analysis_by_trace_id(self, trace_id: str) -> Optional[AnalysisResult]:
        """根据trace_id获取分析结果"""
        try:
            doc = await self.collection.find_one(
                {"trace_id": trace_id},
                sort=[("created_at", -1)]  # 获取最新的分析结果
            )
            if doc:
                doc.pop("_id", None)
                return AnalysisResult.from_dict(doc)
            return None
            
        except Exception as e:
            logger.error(f"根据trace_id获取分析结果失败: {str(e)}")
            raise
    
    async def update_analysis_result(
        self,
        analysis_id: str,
        analysis_results: AnalysisResults,
        status: str = "completed"
    ) -> bool:
        """更新分析结果"""
        try:
            update_data = {
                "analysis_results": analysis_results.dict(),
                "status": status,
                "completed_at": datetime.utcnow()
            }
            
            result = await self.collection.update_one(
                {"analysis_id": analysis_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"更新分析结果失败: {str(e)}")
            raise
    
    async def update_analysis_error(self, analysis_id: str, error_message: str) -> bool:
        """更新分析错误状态"""
        try:
            update_data = {
                "status": "failed",
                "error_message": error_message,
                "completed_at": datetime.utcnow()
            }
            
            result = await self.collection.update_one(
                {"analysis_id": analysis_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"更新分析错误状态失败: {str(e)}")
            raise
    
    async def get_analysis_history(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[AnalysisResult], int]:
        """获取分析历史"""
        try:
            query = filters or {}
            
            # 计算总数
            total = await self.collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * size
            cursor = self.collection.find(query).skip(skip).limit(size).sort("created_at", -1)
            
            analyses = []
            async for doc in cursor:
                doc.pop("_id", None)
                analyses.append(AnalysisResult.from_dict(doc))
            
            return analyses, total
            
        except Exception as e:
            logger.error(f"获取分析历史失败: {str(e)}")
            raise
    
    async def get_optimization_suggestions_summary(
        self,
        project_key: str,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取优化建议汇总"""
        try:
            # 构建聚合管道
            match_stage = {
                "project_key": project_key,
                "status": "completed",
                "analysis_results": {"$exists": True, "$ne": None}
            }
            
            pipeline = [
                {"$match": match_stage},
                {"$unwind": "$analysis_results.optimization_suggestions"},
                {
                    "$group": {
                        "_id": {
                            "category": "$analysis_results.optimization_suggestions.category",
                            "title": "$analysis_results.optimization_suggestions.title"
                        },
                        "suggestion": {"$first": "$analysis_results.optimization_suggestions"},
                        "count": {"$sum": 1},
                        "latest_analysis": {"$max": "$created_at"}
                    }
                },
                {"$sort": {"count": -1, "latest_analysis": -1}},
                {"$limit": limit}
            ]
            
            # 添加过滤条件
            if category:
                pipeline.insert(1, {
                    "$match": {"analysis_results.optimization_suggestions.category": category}
                })
            
            if priority:
                pipeline.insert(-2, {
                    "$match": {"suggestion.priority": priority}
                })
            
            # 执行聚合查询
            cursor = self.collection.aggregate(pipeline)
            suggestions = []
            
            async for doc in cursor:
                suggestion_data = doc["suggestion"]
                suggestion_data["frequency"] = doc["count"]
                suggestion_data["latest_seen"] = doc["latest_analysis"]
                suggestions.append(suggestion_data)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"获取优化建议汇总失败: {str(e)}")
            raise
    
    async def get_bottleneck_statistics(self, project_key: str) -> Dict[str, Any]:
        """获取性能瓶颈统计"""
        try:
            pipeline = [
                {
                    "$match": {
                        "project_key": project_key,
                        "status": "completed",
                        "analysis_results": {"$exists": True, "$ne": None}
                    }
                },
                {"$unwind": "$analysis_results.bottleneck_analysis"},
                {
                    "$group": {
                        "_id": "$analysis_results.bottleneck_analysis.type",
                        "count": {"$sum": 1},
                        "avg_impact": {"$avg": "$analysis_results.bottleneck_analysis.impact"},
                        "max_impact": {"$max": "$analysis_results.bottleneck_analysis.impact"},
                        "severity_counts": {
                            "$push": "$analysis_results.bottleneck_analysis.severity"
                        }
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            bottleneck_stats = []
            
            async for doc in cursor:
                # 统计严重程度分布
                severity_counts = {}
                for severity in doc["severity_counts"]:
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                bottleneck_stats.append({
                    "type": doc["_id"],
                    "count": doc["count"],
                    "avg_impact": round(doc["avg_impact"], 3),
                    "max_impact": round(doc["max_impact"], 3),
                    "severity_distribution": severity_counts
                })
            
            return {
                "bottleneck_types": bottleneck_stats,
                "total_analyses": len(bottleneck_stats),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取瓶颈统计失败: {str(e)}")
            raise