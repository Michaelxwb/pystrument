"""
项目管理服务
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from app.config.database import get_database
from app.models.project import Project, ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


class ProjectService:
    """项目管理服务类"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db.projects if self.db else None
    
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """创建新项目"""
        try:
            # 生成项目密钥
            project_key = Project.generate_project_key()
            
            # 创建项目实例
            project = Project(
                project_key=project_key,
                name=project_data.name,
                description=project_data.description,
                framework=project_data.framework,
                config=project_data.config,
                status="active"
            )
            
            # 保存到数据库
            await self.collection.insert_one(project.to_dict())
            
            logger.info(f"创建项目成功: {project.name} ({project_key})")
            return project
            
        except Exception as e:
            logger.error(f"创建项目失败: {str(e)}")
            raise
    
    async def get_project_by_key(self, project_key: str) -> Optional[Project]:
        """根据项目密钥获取项目"""
        try:
            doc = await self.collection.find_one({"project_key": project_key})
            if doc:
                doc.pop("_id", None)
                return Project.from_dict(doc)
            return None
            
        except Exception as e:
            logger.error(f"获取项目失败: {str(e)}")
            raise
    
    async def get_project_by_name(self, name: str) -> Optional[Project]:
        """根据项目名称获取项目"""
        try:
            doc = await self.collection.find_one({"name": name})
            if doc:
                doc.pop("_id", None)
                return Project.from_dict(doc)
            return None
            
        except Exception as e:
            logger.error(f"根据名称获取项目失败: {str(e)}")
            raise
    
    async def get_projects(
        self, 
        page: int = 1, 
        size: int = 10, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Project], int]:
        """获取项目列表"""
        try:
            # 构建查询条件
            query = filters or {}
            
            # 计算总数
            total = await self.collection.count_documents(query)
            
            # 分页查询
            skip = (page - 1) * size
            cursor = self.collection.find(query).skip(skip).limit(size).sort("created_at", -1)
            
            projects = []
            async for doc in cursor:
                doc.pop("_id", None)
                projects.append(Project.from_dict(doc))
            
            return projects, total
            
        except Exception as e:
            logger.error(f"获取项目列表失败: {str(e)}")
            raise
    
    async def update_project(self, project_key: str, project_data: ProjectUpdate) -> Project:
        """更新项目信息"""
        try:
            # 构建更新数据
            update_data = {}
            if project_data.name is not None:
                update_data["name"] = project_data.name
            if project_data.description is not None:
                update_data["description"] = project_data.description
            if project_data.framework is not None:
                update_data["framework"] = project_data.framework
            if project_data.status is not None:
                update_data["status"] = project_data.status
            if project_data.config is not None:
                update_data["config"] = project_data.config.dict()
            
            update_data["updated_at"] = datetime.utcnow()
            
            # 更新数据库
            await self.collection.update_one(
                {"project_key": project_key},
                {"$set": update_data}
            )
            
            # 返回更新后的项目
            return await self.get_project_by_key(project_key)
            
        except Exception as e:
            logger.error(f"更新项目失败: {str(e)}")
            raise
    
    async def archive_project(self, project_key: str) -> bool:
        """归档项目（软删除）"""
        try:
            result = await self.collection.update_one(
                {"project_key": project_key},
                {
                    "$set": {
                        "status": "archived",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"归档项目失败: {str(e)}")
            raise
    
    async def update_last_activity(self, project_key: str) -> bool:
        """更新项目最后活跃时间"""
        try:
            result = await self.collection.update_one(
                {"project_key": project_key},
                {"$set": {"last_activity": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"更新项目活跃时间失败: {str(e)}")
            return False
    
    async def get_project_stats(self, project_key: str) -> Dict[str, Any]:
        """获取项目统计信息"""
        try:
            # 从性能记录集合获取统计数据
            performance_collection = self.db.performance_records
            analysis_collection = self.db.ai_analysis_results
            
            # 总请求数
            total_requests = await performance_collection.count_documents(
                {"project_key": project_key}
            )
            
            # 今日请求数
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_requests = await performance_collection.count_documents({
                "project_key": project_key,
                "timestamp": {"$gte": today_start}
            })
            
            # 平均响应时间
            pipeline = [
                {"$match": {"project_key": project_key}},
                {"$group": {
                    "_id": None,
                    "avg_duration": {"$avg": "$performance_metrics.total_duration"},
                    "max_duration": {"$max": "$performance_metrics.total_duration"}
                }}
            ]
            
            avg_stats = await performance_collection.aggregate(pipeline).to_list(1)
            avg_duration = avg_stats[0]["avg_duration"] if avg_stats else 0
            max_duration = avg_stats[0]["max_duration"] if avg_stats else 0
            
            # AI分析次数
            analysis_count = await analysis_collection.count_documents(
                {"project_key": project_key}
            )
            
            return {
                "total_requests": total_requests,
                "today_requests": today_requests,
                "avg_response_time": round(avg_duration, 3) if avg_duration else 0,
                "max_response_time": round(max_duration, 3) if max_duration else 0,
                "analysis_count": analysis_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取项目统计信息失败: {str(e)}")
            raise