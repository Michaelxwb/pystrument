## 4.3 MongoDB数据模型设计

### 4.3.1 项目管理集合 (projects)
**用途**: 管理接入的第三方项目信息，提供项目维度的性能监控管理
```python
{
    "_id": ObjectId,                    # MongoDB主键
    "project_key": str,                 # 项目唯一标识键，用于SDK接入认证
    "name": str,                        # 项目名称，如"用户管理系统API"
    "description": str,                 # 项目描述信息
    "framework": str,                   # 项目技术框架：flask/django/fastapi
    "status": str,                      # 项目状态：active/inactive/archived
    "config": {                         # 项目配置信息
        "sampling_rate": float,         # 性能采样率：0.0-1.0
        "enabled": bool,                # 是否启用监控
        "auto_analysis": bool,          # 是否启用自动AI分析
        "alert_threshold": {            # 告警阈值配置
            "response_time": float,     # 响应时间告警阈值（秒）
            "error_rate": float,        # 错误率告警阈值
            "memory_usage": int         # 内存使用告警阈值（MB）
        }
    },
    "created_at": datetime,             # 创建时间
    "updated_at": datetime,             # 最后更新时间
    "last_activity": datetime           # 最后活跃时间（接收到数据的时间）
}
```

### 4.3.2 性能记录集合 (performance_records)
**用途**: 存储每次接口调用的性能分析数据，支持历史版本管理和性能趋势分析
```python
{
    "_id": ObjectId,                    # MongoDB主键
    "project_key": str,                 # 关联项目标识
    "trace_id": str,                    # 调用链路唯一标识
    "request_info": {                   # 请求基本信息
        "method": str,                  # HTTP方法：GET/POST/PUT/DELETE
        "path": str,                    # 请求路径：/api/users/123
        "query_params": dict,           # 查询参数
        "headers": dict,                # 请求头信息（过滤敏感信息）
        "user_agent": str,              # 用户代理
        "remote_ip": str                # 客户端IP地址
    },
    "response_info": {                  # 响应信息
        "status_code": int,             # HTTP状态码
        "response_size": int,           # 响应体大小（字节）
        "content_type": str             # 响应内容类型
    },
    "performance_metrics": {            # 性能指标
        "total_duration": float,        # 总耗时（秒）
        "cpu_time": float,              # CPU时间（秒）
        "memory_usage": {               # 内存使用情况
            "peak_memory": int,         # 峰值内存使用（MB）
            "memory_delta": int         # 内存变化量（MB）
        },
        "database_metrics": {           # 数据库性能指标
            "query_count": int,         # SQL查询次数
            "query_time": float,        # SQL总耗时（秒）
            "slow_queries": int         # 慢查询次数
        },
        "cache_metrics": {              # 缓存性能指标
            "cache_hits": int,          # 缓存命中次数
            "cache_misses": int,        # 缓存未命中次数
            "cache_time": float         # 缓存操作总耗时（秒）
        }
    },
    "function_calls": [                 # 函数调用链路（引用 function_calls 集合）
        {
            "call_id": str,             # 函数调用唯一标识
            "function_name": str,       # 函数名称
            "file_path": str,           # 文件路径
            "line_number": int,         # 行号
            "duration": float,          # 函数执行耗时（秒）
            "parent_call_id": str,      # 父函数调用ID（用于构建调用树）
            "depth": int,               # 调用深度
            "call_order": int           # 调用顺序
        }
    ],
    "version_info": {                   # 版本信息
        "app_version": str,             # 应用版本号
        "git_commit": str,              # Git提交哈希
        "deploy_time": datetime         # 部署时间
    },
    "environment": {                    # 运行环境信息
        "python_version": str,          # Python版本
        "framework_version": str,       # 框架版本
        "server_info": str              # 服务器信息
    },
    "timestamp": datetime,              # 记录时间戳
    "created_at": datetime              # 创建时间
}
```

### 4.3.3 函数调用详情集合 (function_calls)
**用途**: 存储详细的函数调用链路信息，支持深度性能分析和调用栈追踪
```python
{
    "_id": ObjectId,                    # MongoDB主键
    "trace_id": str,                    # 关联的调用链路标识
    "call_id": str,                     # 函数调用唯一标识
    "parent_call_id": str,              # 父函数调用ID，用于构建调用树
    "function_info": {                  # 函数基本信息
        "name": str,                    # 函数名称：get_user_by_id
        "module": str,                  # 模块名称：app.services.user_service
        "file_path": str,               # 文件完整路径
        "line_number": int,             # 函数定义行号
        "class_name": str               # 所属类名（如果是类方法）
    },
    "execution_info": {                 # 执行信息
        "start_time": datetime,         # 函数开始执行时间
        "end_time": datetime,           # 函数结束执行时间
        "duration": float,              # 执行耗时（秒）
        "cpu_time": float,              # CPU时间（秒）
        "memory_delta": int             # 内存变化量（字节）
    },
    "call_context": {                   # 调用上下文
        "depth": int,                   # 调用深度（从0开始）
        "call_order": int,              # 在整个调用链中的顺序
        "is_recursive": bool,           # 是否为递归调用
        "exception_info": str           # 异常信息（如果有）
    },
    "performance_tags": [str],          # 性能标签：slow/database/cache/external_api
    "created_at": datetime              # 创建时间
}
```

### 4.3.4 AI分析结果集合 (ai_analysis_results)
**用途**: 存储AI对性能数据的分析结果和优化建议，支持分析历史管理
```python
{
    "_id": ObjectId,                    # MongoDB主键
    "project_key": str,                 # 关联项目标识
    "trace_id": str,                    # 关联的性能记录ID
    "analysis_type": str,               # 分析类型：auto/manual/scheduled
    "ai_service": {                     # AI服务信息
        "provider": str,                # AI服务提供商：openai/custom
        "model": str,                   # 使用的模型：gpt-4/claude-3
        "version": str                  # 模型版本
    },
    "analysis_input": {                 # 分析输入数据
        "performance_summary": dict,    # 性能数据摘要
        "slow_functions": list,         # 慢函数列表
        "context_info": dict            # 上下文信息
    },
    "analysis_results": {               # AI分析结果
        "performance_score": float,     # 性能评分：0-100
        "bottleneck_analysis": [        # 性能瓶颈分析
            {
                "type": str,            # 瓶颈类型：database/computation/io/memory
                "severity": str,        # 严重程度：critical/high/medium/low
                "function": str,        # 相关函数
                "description": str,     # 瓶颈描述
                "impact": float         # 影响程度（耗时占比）
            }
        ],
        "optimization_suggestions": [   # 优化建议
            {
                "category": str,        # 建议类别：database/caching/algorithm/architecture
                "priority": str,        # 优先级：high/medium/low
                "title": str,           # 建议标题
                "description": str,     # 详细描述
                "code_example": str,    # 代码示例
                "expected_improvement": str  # 预期改进效果
            }
        ],
        "risk_assessment": {            # 风险评估
            "current_risks": [str],     # 当前风险点
            "potential_issues": [str],  # 潜在问题
            "recommendations": [str]    # 风险建议
        }
    },
    "analysis_metadata": {              # 分析元数据
        "duration": float,              # 分析耗时（秒）
        "confidence_score": float,      # 分析可信度：0-1
        "tokens_used": int,             # 使用的token数量
        "cost": float                   # 分析成本
    },
    "status": str,                      # 分析状态：pending/completed/failed
    "created_at": datetime,             # 创建时间
    "completed_at": datetime            # 完成时间
}
```

### 4.3.5 系统配置集合 (system_config)
**用途**: 存储系统级配置信息，支持动态配置更新
```python
{
    "_id": ObjectId,                    # MongoDB主键
    "config_key": str,                  # 配置键名：ai_service/alert_rules/system_limits
    "config_value": dict,               # 配置值（JSON格式）
    "description": str,                 # 配置描述
    "category": str,                    # 配置分类：ai/monitoring/system
    "is_active": bool,                  # 是否激活
    "created_at": datetime,             # 创建时间
    "updated_at": datetime              # 更新时间
}
```