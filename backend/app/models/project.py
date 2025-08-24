"""
项目数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class ProjectConfig(BaseModel):
    """项目配置模型"""
    sampling_rate: float = Field(default=0.3, ge=0.0, le=1.0, description="性能采样率")
    enabled: bool = Field(default=True, description="是否启用监控")
    auto_analysis: bool = Field(default=False, description="是否启用自动AI分析")
    alert_threshold: Dict[str, Any] = Field(
        default={
            "response_time": 2.0,
            "error_rate": 0.05,
            "memory_usage": 512
        },
        description="告警阈值配置"
    )


class ProjectBase(BaseModel):
    """项目基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, max_length=500, description="项目描述")
    framework: str = Field(..., description="技术框架")
    base_url: Optional[str] = Field(None, description="项目基础URL")


class ProjectCreate(ProjectBase):
    """创建项目请求模型"""
    config: Optional[ProjectConfig] = Field(default_factory=ProjectConfig, description="项目配置")


class ProjectUpdate(BaseModel):
    """更新项目请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, max_length=500, description="项目描述")
    framework: Optional[str] = Field(None, description="技术框架")
    base_url: Optional[str] = Field(None, description="项目基础URL")
    status: Optional[str] = Field(None, description="项目状态")
    config: Optional[ProjectConfig] = Field(None, description="项目配置")


class Project(ProjectBase):
    """项目完整模型"""
    project_key: str = Field(..., description="项目唯一标识键")
    status: str = Field(default="active", description="项目状态")
    config: ProjectConfig = Field(default_factory=ProjectConfig, description="项目配置")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    last_activity: Optional[datetime] = Field(None, description="最后活跃时间")
    
    @classmethod
    def generate_project_key(cls) -> str:
        """生成项目密钥"""
        return f"proj_{uuid.uuid4().hex[:16]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "project_key": self.project_key,
            "name": self.name,
            "description": self.description,
            "framework": self.framework,
            "base_url": self.base_url,
            "status": self.status,
            "config": self.config.dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_activity": self.last_activity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """从字典创建实例"""
        if "config" in data and isinstance(data["config"], dict):
            data["config"] = ProjectConfig(**data["config"])
        return cls(**data)