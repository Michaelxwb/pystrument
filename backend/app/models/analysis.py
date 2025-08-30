"""
AI分析相关数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AnalysisPriority(str, Enum):
    """分析优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class AnalysisStatus(str, Enum):
    """分析状态"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CANCELED = "CANCELED"


class BottleneckAnalysis(BaseModel):
    """瓶颈分析模型"""
    type: str = Field(..., description="瓶颈类型")
    severity: str = Field(..., description="严重程度")
    function: str = Field(..., description="相关函数")
    description: str = Field(..., description="描述")
    impact: float = Field(..., description="影响程度(0-1)")


class OptimizationSuggestion(BaseModel):
    """优化建议模型"""
    category: str = Field(..., description="建议类别")
    priority: str = Field(..., description="优先级")
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    code_example: Optional[str] = Field(None, description="代码示例")
    expected_improvement: Optional[str] = Field(None, description="预期改进")


class RiskAssessment(BaseModel):
    """风险评估模型"""
    current_risks: List[str] = Field(default=[], description="当前风险")
    potential_issues: List[str] = Field(default=[], description="潜在问题")
    recommendations: List[str] = Field(default=[], description="建议")


class AnalysisResults(BaseModel):
    """分析结果模型"""
    performance_score: float = Field(..., description="性能评分(0-100)")
    bottleneck_analysis: List[BottleneckAnalysis] = Field(default=[], description="性能瓶颈分析")
    optimization_suggestions: List[OptimizationSuggestion] = Field(default=[], description="优化建议")
    risk_assessment: RiskAssessment = Field(default=RiskAssessment(), description="风险评估")
    summary: Optional[str] = Field(None, description="分析总结")


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    ai_service: str = Field(default="default", description="AI服务名称")
    priority: AnalysisPriority = Field(default=AnalysisPriority.NORMAL, description="任务优先级")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="自定义分析参数")


class BatchAnalysisRequest(BaseModel):
    """批量分析请求模型"""
    project_key: str = Field(..., description="项目标识")
    record_ids: List[str] = Field(..., description="性能记录ID列表")
    ai_service: str = Field(default="default", description="AI服务名称")
    priority: AnalysisPriority = Field(default=AnalysisPriority.NORMAL, description="任务优先级")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="自定义分析参数")


class TaskStatus(BaseModel):
    """任务状态模型"""
    task_id: str = Field(..., description="任务ID")
    status: AnalysisStatus = Field(..., description="任务状态")
    progress: int = Field(default=0, description="进度百分比")
    analysis_id: Optional[str] = Field(None, description="关联的分析ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    estimated_completion: Optional[datetime] = Field(None, description="预计完成时间")
    error: Optional[str] = Field(None, description="错误信息")


class AnalysisRecord(BaseModel):
    """分析记录模型"""
    analysis_id: str = Field(..., description="分析ID")
    performance_record_id: str = Field(..., description="关联的性能记录ID")
    project_key: str = Field(..., description="项目标识")
    ai_service: str = Field(..., description="AI服务名称")
    status: AnalysisStatus = Field(..., description="分析状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    results: Optional[AnalysisResults] = Field(None, description="分析结果")
    task_id: str = Field(..., description="关联的任务ID")
    priority: AnalysisPriority = Field(..., description="任务优先级")
    analysis_type: Optional[str] = Field("ai_analysis", description="分析类型")