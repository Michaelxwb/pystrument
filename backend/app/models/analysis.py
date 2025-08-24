"""
AI分析数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class BottleneckAnalysis(BaseModel):
    """性能瓶颈分析模型"""
    type: str = Field(..., description="瓶颈类型")
    severity: str = Field(..., description="严重程度")
    function: str = Field(..., description="相关函数")
    description: str = Field(..., description="瓶颈描述")
    impact: float = Field(..., ge=0, le=1, description="影响程度（耗时占比）")


class OptimizationSuggestion(BaseModel):
    """优化建议模型"""
    category: str = Field(..., description="建议类别")
    priority: str = Field(..., description="优先级")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="详细描述")
    code_example: Optional[str] = Field(None, description="代码示例")
    expected_improvement: Optional[str] = Field(None, description="预期改进效果")


class RiskAssessment(BaseModel):
    """风险评估模型"""
    current_risks: List[str] = Field(default_factory=list, description="当前风险点")
    potential_issues: List[str] = Field(default_factory=list, description="潜在问题")
    recommendations: List[str] = Field(default_factory=list, description="风险建议")


class AIService(BaseModel):
    """AI服务信息模型"""
    provider: str = Field(..., description="AI服务提供商")
    model: str = Field(..., description="使用的模型")
    version: Optional[str] = Field(None, description="模型版本")


class AnalysisInput(BaseModel):
    """分析输入数据模型"""
    performance_summary: Dict[str, Any] = Field(default_factory=dict, description="性能数据摘要")
    slow_functions: List[Dict[str, Any]] = Field(default_factory=list, description="慢函数列表")
    context_info: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class AnalysisResults(BaseModel):
    """AI分析结果模型"""
    performance_score: float = Field(..., ge=0, le=100, description="性能评分")
    bottleneck_analysis: List[BottleneckAnalysis] = Field(default_factory=list, description="瓶颈分析")
    optimization_suggestions: List[OptimizationSuggestion] = Field(default_factory=list, description="优化建议")
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment, description="风险评估")


class AnalysisMetadata(BaseModel):
    """分析元数据模型"""
    duration: float = Field(default=0.0, ge=0, description="分析耗时（秒）")
    confidence_score: float = Field(default=0.0, ge=0, le=1, description="分析可信度")
    tokens_used: int = Field(default=0, ge=0, description="使用的token数量")
    cost: float = Field(default=0.0, ge=0, description="分析成本")


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    trace_id: str = Field(..., description="性能记录ID")
    analysis_type: str = Field(default="manual", description="分析类型")
    ai_service: str = Field(default="openai", description="AI服务")


class AnalysisResult(BaseModel):
    """AI分析结果完整模型"""
    analysis_id: str = Field(..., description="分析任务ID")
    project_key: str = Field(..., description="关联项目标识")
    trace_id: str = Field(..., description="关联的性能记录ID")
    analysis_type: str = Field(..., description="分析类型")
    ai_service: AIService = Field(..., description="AI服务信息")
    analysis_input: AnalysisInput = Field(default_factory=AnalysisInput, description="分析输入数据")
    analysis_results: Optional[AnalysisResults] = Field(None, description="AI分析结果")
    analysis_metadata: AnalysisMetadata = Field(default_factory=AnalysisMetadata, description="分析元数据")
    status: str = Field(default="pending", description="分析状态")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    
    @classmethod
    def generate_analysis_id(cls) -> str:
        """生成分析任务ID"""
        return f"analysis_{uuid.uuid4().hex[:16]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "analysis_id": self.analysis_id,
            "project_key": self.project_key,
            "trace_id": self.trace_id,
            "analysis_type": self.analysis_type,
            "ai_service": self.ai_service.dict(),
            "analysis_input": self.analysis_input.dict(),
            "analysis_results": self.analysis_results.dict() if self.analysis_results else None,
            "analysis_metadata": self.analysis_metadata.dict(),
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """从字典创建实例"""
        # 转换嵌套模型
        if "ai_service" in data:
            data["ai_service"] = AIService(**data["ai_service"])
        if "analysis_input" in data:
            data["analysis_input"] = AnalysisInput(**data["analysis_input"])
        if "analysis_results" in data and data["analysis_results"]:
            # 转换分析结果中的嵌套模型
            results_data = data["analysis_results"]
            if "bottleneck_analysis" in results_data:
                results_data["bottleneck_analysis"] = [
                    BottleneckAnalysis(**ba) for ba in results_data["bottleneck_analysis"]
                ]
            if "optimization_suggestions" in results_data:
                results_data["optimization_suggestions"] = [
                    OptimizationSuggestion(**os) for os in results_data["optimization_suggestions"]
                ]
            if "risk_assessment" in results_data:
                results_data["risk_assessment"] = RiskAssessment(**results_data["risk_assessment"])
            data["analysis_results"] = AnalysisResults(**results_data)
        if "analysis_metadata" in data:
            data["analysis_metadata"] = AnalysisMetadata(**data["analysis_metadata"])
        
        return cls(**data)


class SystemConfig(BaseModel):
    """系统配置模型"""
    config_key: str = Field(..., description="配置键名")
    config_value: Dict[str, Any] = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")
    category: str = Field(..., description="配置分类")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "config_key": self.config_key,
            "config_value": self.config_value,
            "description": self.description,
            "category": self.category,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }