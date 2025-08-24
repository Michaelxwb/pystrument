"""
性能记录数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class FunctionCall(BaseModel):
    """函数调用模型"""
    call_id: str = Field(..., description="函数调用唯一标识")
    parent_call_id: Optional[str] = Field(None, description="父函数调用ID")
    function_name: str = Field(..., description="函数名称")
    file_path: str = Field(..., description="文件路径")
    line_number: int = Field(..., description="行号")
    duration: float = Field(..., ge=0, description="函数执行耗时（秒）")
    depth: int = Field(..., ge=0, description="调用深度")
    call_order: int = Field(..., ge=0, description="调用顺序")


class RequestInfo(BaseModel):
    """请求信息模型"""
    method: str = Field(..., description="HTTP方法")
    path: str = Field(..., description="请求路径")
    query_params: Dict[str, Any] = Field(default_factory=dict, description="查询参数")
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    user_agent: Optional[str] = Field(None, description="用户代理")
    remote_ip: Optional[str] = Field(None, description="客户端IP")


class ResponseInfo(BaseModel):
    """响应信息模型"""
    status_code: int = Field(..., description="HTTP状态码")
    response_size: int = Field(default=0, ge=0, description="响应体大小（字节）")
    content_type: Optional[str] = Field(None, description="响应内容类型")


class MemoryUsage(BaseModel):
    """内存使用模型"""
    peak_memory: int = Field(default=0, ge=0, description="峰值内存使用（MB）")
    memory_delta: int = Field(default=0, description="内存变化量（MB）")


class DatabaseMetrics(BaseModel):
    """数据库性能指标模型"""
    query_count: int = Field(default=0, ge=0, description="SQL查询次数")
    query_time: float = Field(default=0.0, ge=0, description="SQL总耗时（秒）")
    slow_queries: int = Field(default=0, ge=0, description="慢查询次数")


class CacheMetrics(BaseModel):
    """缓存性能指标模型"""
    cache_hits: int = Field(default=0, ge=0, description="缓存命中次数")
    cache_misses: int = Field(default=0, ge=0, description="缓存未命中次数")
    cache_time: float = Field(default=0.0, ge=0, description="缓存操作总耗时（秒）")


class PerformanceMetrics(BaseModel):
    """性能指标模型"""
    total_duration: float = Field(..., ge=0, description="总耗时（秒）")
    cpu_time: float = Field(default=0.0, ge=0, description="CPU时间（秒）")
    memory_usage: MemoryUsage = Field(default_factory=MemoryUsage, description="内存使用情况")
    database_metrics: DatabaseMetrics = Field(default_factory=DatabaseMetrics, description="数据库指标")
    cache_metrics: CacheMetrics = Field(default_factory=CacheMetrics, description="缓存指标")


class VersionInfo(BaseModel):
    """版本信息模型"""
    app_version: Optional[str] = Field(None, description="应用版本号")
    git_commit: Optional[str] = Field(None, description="Git提交哈希")
    deploy_time: Optional[datetime] = Field(None, description="部署时间")


class Environment(BaseModel):
    """运行环境信息模型"""
    python_version: Optional[str] = Field(None, description="Python版本")
    framework_version: Optional[str] = Field(None, description="框架版本")
    server_info: Optional[str] = Field(None, description="服务器信息")


class PerformanceRecordCreate(BaseModel):
    """创建性能记录请求模型"""
    trace_id: str = Field(..., description="调用链路唯一标识")
    request_info: RequestInfo = Field(..., description="请求信息")
    response_info: ResponseInfo = Field(..., description="响应信息")
    performance_metrics: PerformanceMetrics = Field(..., description="性能指标")
    function_calls: List[FunctionCall] = Field(default_factory=list, description="函数调用链路")
    version_info: Optional[VersionInfo] = Field(None, description="版本信息")
    environment: Optional[Environment] = Field(None, description="环境信息")


class PerformanceRecord(PerformanceRecordCreate):
    """性能记录完整模型"""
    project_key: str = Field(..., description="关联项目标识")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="记录时间戳")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "project_key": self.project_key,
            "trace_id": self.trace_id,
            "request_info": self.request_info.dict(),
            "response_info": self.response_info.dict(),
            "performance_metrics": self.performance_metrics.dict(),
            "function_calls": [fc.dict() for fc in self.function_calls],
            "version_info": self.version_info.dict() if self.version_info else None,
            "environment": self.environment.dict() if self.environment else None,
            "timestamp": self.timestamp,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceRecord":
        """从字典创建实例"""
        # 转换嵌套模型
        if "request_info" in data:
            data["request_info"] = RequestInfo(**data["request_info"])
        if "response_info" in data:
            data["response_info"] = ResponseInfo(**data["response_info"])
        if "performance_metrics" in data:
            data["performance_metrics"] = PerformanceMetrics(**data["performance_metrics"])
        if "function_calls" in data:
            data["function_calls"] = [FunctionCall(**fc) for fc in data["function_calls"]]
        if "version_info" in data and data["version_info"]:
            data["version_info"] = VersionInfo(**data["version_info"])
        if "environment" in data and data["environment"]:
            data["environment"] = Environment(**data["environment"])
        
        return cls(**data)


class FunctionCallDetail(BaseModel):
    """函数调用详情模型"""
    trace_id: str = Field(..., description="关联的调用链路标识")
    call_id: str = Field(..., description="函数调用唯一标识")
    parent_call_id: Optional[str] = Field(None, description="父函数调用ID")
    function_info: Dict[str, Any] = Field(..., description="函数基本信息")
    execution_info: Dict[str, Any] = Field(..., description="执行信息")
    call_context: Dict[str, Any] = Field(..., description="调用上下文")
    performance_tags: List[str] = Field(default_factory=list, description="性能标签")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "trace_id": self.trace_id,
            "call_id": self.call_id,
            "parent_call_id": self.parent_call_id,
            "function_info": self.function_info,
            "execution_info": self.execution_info,
            "call_context": self.call_context,
            "performance_tags": self.performance_tags,
            "created_at": self.created_at
        }