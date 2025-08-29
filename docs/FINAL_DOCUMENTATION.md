# 基于Pyinstrument的性能分析平台 - 完整文档

## 目录
1. [项目概述](#1-项目概述)
2. [技术架构](#2-技术架构)
3. [核心功能](#3-核心功能)
4. [快速开始](#4-快速开始)
5. [SDK使用指南](#5-sdk使用指南)
6. [API接口文档](#6-api接口文档)
7. [项目结构](#7-项目结构)
8. [部署配置](#8-部署配置)
9. [AI分析服务](#9-ai分析服务)
10. [Celery任务队列](#10-celery任务队列)
11. [测试与质量保证](#11-测试与质量保证)
12. [故障排除](#12-故障排除)

---

## 1. 项目概述

这是一个基于pyinstrument的性能分析平台，提供插件式的快速接入方案，支持自动监控全平台接口性能，记录函数级执行链路，并集成AI工具进行自动化性能分析和优化建议。

### 核心特性

- 🚀 **快速接入**: 支持Flask、Django、FastAPI等多种框架的零代码或最小代码接入
- 📊 **实时监控**: 自动监控接口性能，记录详细的函数调用链路
- 🤖 **AI分析**: 集成AI工具自动分析性能瓶颈，提供优化建议
- 📈 **可视化界面**: Vue3前端管理界面，支持性能数据可视化
- 🔄 **历史版本管理**: 支持查看历史版本的接口性能数据对比
- 🛡️ **插件式设计**: 不影响目标项目的正常功能

---

## 2. 技术架构

### 2.1 后端技术栈
- **框架**: FastAPI (高性能异步Web框架)
- **数据库**: MongoDB (主数据库) + Redis (缓存)
- **性能分析**: pyinstrument
- **任务队列**: Celery + Redis
- **AI集成**: 支持OpenAI API、自定义AI服务

### 2.2 前端技术栈
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **图表可视化**: ECharts
- **构建工具**: Vite

### 2.3 SDK组件
- **Python SDK**: 支持Flask、Django、FastAPI等Web框架
- **配置管理**: YAML/JSON配置文件
- **数据传输**: HTTP REST API

### 2.4 开发环境
- **Node.js**: v24.3.0+
- **npm**: 11.4.2+
- **Python**: 3.9.6+
- **pip3**: 25.1.1+

---

## 3. 核心功能

### 3.1 统一响应体封装

#### 响应体结构设计
``python
# 标准响应体结构
{
    "code": 0,           # 状态码：0-成功，非0-失败
    "msg": "success",    # 消息描述
    "data": {}           # 业务数据
}
```

#### 错误码设计
``python
# 系统级错误码
SUCCESS = 0                    # 成功
SYSTEM_ERROR = 10000          # 系统错误
PARAMETER_ERROR = 10001       # 参数错误
AUTHENTICATION_ERROR = 10002  # 认证错误
PERMISSION_ERROR = 10003      # 权限错误
RATE_LIMIT_ERROR = 10004      # 频率限制
DATABASE_ERROR = 10005        # 数据库错误

# 业务级错误码
PROJECT_NOT_FOUND = 20001     # 项目不存在
PROJECT_NAME_EXISTS = 20002   # 项目名称已存在
INVALID_PROJECT_KEY = 20003   # 无效的项目密钥
PERFORMANCE_DATA_INVALID = 20004  # 性能数据无效
AI_SERVICE_UNAVAILABLE = 20005    # AI服务不可用
ANALYSIS_IN_PROGRESS = 20006      # 分析正在进行中
```

### 3.2 数据模型设计

#### 项目管理集合 (projects)
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

#### 性能记录集合 (performance_records)
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

#### AI分析结果集合 (ai_analysis_results)
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

---

## 4. 快速开始

### 环境要求

- Node.js: v24.3.0+
- npm: 11.4.2+
- Python: 3.9.6+
- pip3: 25.1.1+
- Docker & Docker Compose

### 1. 克隆项目

```bash
git clone <repository-url>
cd pystrument
```

### 2. 启动服务

#### 使用Docker Compose (推荐)

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

#### 手动启动

```bash
# 1. 启动MongoDB和Redis
docker-compose up -d mongodb redis

# 2. 安装后端依赖
cd backend
pip3 install -r requirements.txt

# 3. 启动后端服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. 安装前端依赖
cd ../frontend
npm install

# 5. 启动前端服务
npm run dev
```

### 3. 访问服务

- 前端管理界面: http://localhost:3000
- 后端API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

---

## 5. SDK使用指南

### 5.1 Flask应用接入

#### 方式一：中间件接入（推荐）

```python
from flask import Flask
from performance_monitor.flask.middleware import PerformanceMiddleware
from performance_monitor.utils.config import Config

app = Flask(__name__)

# 配置性能监控
config = Config({
    'project_key': 'your_project_key',
    'api_endpoint': 'http://localhost:8000',
    'enabled': True,
    'sampling_rate': 10.0,  # 10%采样率
    'async_send': True
})

# 添加中间件
middleware = PerformanceMiddleware(app, config)

@app.route('/api/users')
def get_users():
    # 你的业务逻辑
    return {'users': []}
```

#### 方式二：WSGI包装器（零代码修改）

```python
from performance_monitor.flask.middleware import PerformanceWSGIWrapper
from performance_monitor.utils.config import Config

# 在你的WSGI配置文件中（如wsgi.py）
from your_app import app

config = Config({
    'project_key': 'your_project_key',
    'api_endpoint': 'http://localhost:8000',
    'enabled': True
})

# 包装原有的Flask应用
application = PerformanceWSGIWrapper(app, config)
```

#### 方式三：装饰器接入

```python
from performance_monitor.flask.decorators import monitor_performance

@app.route('/api/critical-endpoint')
@monitor_performance(track_sql=True, track_memory=True)
def critical_endpoint():
    # 重要接口的业务逻辑
    return {'status': 'ok'}
```

### 5.2 Django应用接入

#### 方式一：中间件接入（推荐）

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 在合适位置添加性能监控中间件
    'performance_monitor.django.PerformanceMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... 其他中间件
]

# 性能监控配置
PERFORMANCE_MONITOR = {
    'PROJECT_KEY': os.getenv('PERFORMANCE_MONITOR_PROJECT_KEY'),
    'API_ENDPOINT': 'http://platform.example.com/api',
    'ENABLED': True,
    'SAMPLING_RATE': 0.3,
    'EXCLUDE_PATHS': [
        '/admin/jsi18n/',
        '/static/',
        '/media/',
        '/health/',
        '/favicon.ico'
    ],
    'INCLUDE_PATTERNS': ['/api/', '/admin/'],
    'TRACK_SQL': True,
    'TRACK_CACHE': True,
    'TRACK_TEMPLATES': True,
    'ASYNC_SEND': True
}
```

#### 方式二：装饰器接入

```python
# views.py
from django.shortcuts import render, get_object_or_404
from performance_monitor.django.decorators import monitor_view

@monitor_view(track_sql=True, custom_tags={'api_version': 'v1'})
def user_detail_api(request, user_id):
    """用户详情API"""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile  # 可能触发SQL查询
    recent_orders = user.orders.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    )
    
    return JsonResponse({
        'user': user.to_dict(),
        'profile': profile.to_dict() if profile else None,
        'recent_orders_count': recent_orders.count()
    })
```

### 5.3 FastAPI应用接入

```python
# main.py
from fastapi import FastAPI, Depends
from performance_monitor.fastapi import PerformanceMiddleware

app = FastAPI(title="用户管理API")

# 添加性能监控中间件
app.add_middleware(
    PerformanceMiddleware,
    project_key="your_project_key",
    api_endpoint="http://platform.example.com/api",
    exclude_paths=["/docs", "/redoc", "/openapi.json"],
    sampling_rate=0.3,
    track_request_body=False,  # 避免记录敏感数据
    track_response_body=False
)

@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    """获取用户信息 - 业务代码无需修改"""
    user = await User.get(user_id)
    return user.dict()
```

### 5.4 配置文件

创建配置文件 `performance_config.yaml`:

```yaml
# 基本配置
project_key: "your_project_key"
api_endpoint: "http://localhost:8000"
enabled: true

# 采样配置
sampling_rate: 10.0  # 10%采样率
max_trace_duration: 30.0  # 最大跟踪时长(秒)

# 发送配置
async_send: true
batch_size: 10
batch_timeout: 5
request_timeout: 30

# 过滤配置
excluded_paths:
  - "/health"
  - "/metrics"
  - "/static"

# AI分析配置
enable_ai_analysis: true
ai_analysis_threshold: 1.0  # 响应时间超过1秒时触发AI分析
```

---

## 6. API接口文档

### 6.1 项目管理

```bash
# 创建项目
POST /api/v1/projects
{
  "name": "项目名称",
  "description": "项目描述",
  "framework": "flask",
  "base_url": "http://example.com",
  "sampling_rate": 10.0,
  "enable_ai_analysis": true
}

# 获取项目列表
GET /api/v1/projects?page=1&size=20

# 获取项目详情
GET /api/v1/projects/{project_key}

# 更新项目
PUT /api/v1/projects/{project_key}

# 删除项目
DELETE /api/v1/projects/{project_key}
```

### 6.2 性能数据

```bash
# 提交性能数据
POST /api/v1/performance/collect

# 查询性能记录
GET /api/v1/performance/records?project_key={key}&page=1&size=20

# 获取性能趋势
GET /api/v1/performance/trends/{project_key}?time_range=24h
```

### 6.3 AI分析

```bash
# 触发AI分析
POST /api/v1/analysis/analyze/{performance_record_id}

# 获取分析结果
GET /api/v1/analysis/result/{analysis_id}

# 获取任务状态
GET /api/v1/analysis/task-status/{task_id}

# 获取分析历史
GET /api/v1/analysis/history/{project_key}
```

---

## 7. 项目结构

```
pystrument/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── config/            # 配置管理
│   │   │   ├── __init__.py
│   │   │   ├── settings.py    # 应用配置
│   │   │   └── database.py    # 数据库配置
│   │   ├── middleware/        # 中间件
│   │   │   ├── __init__.py
│   │   │   ├── cors.py        # CORS配置
│   │   │   └── response.py    # 统一响应封装
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── project.py     # 项目模型
│   │   │   ├── performance.py # 性能记录模型
│   │   │   └── analysis.py    # AI分析模型
│   │   ├── api/              # API路由
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── projects.py    # 项目管理接口
│   │   │   │   ├── performance.py # 性能数据接口
│   │   │   │   └── analysis.py    # AI分析接口
│   │   ├── services/         # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── project_service.py
│   │   │   ├── performance_service.py
│   │   │   └── ai_service.py
│   │   ├── utils/            # 工具类
│   │   │   ├── __init__.py
│   │   │   ├── database.py   # 数据库工具
│   │   │   └── response.py   # 响应工具
│   │   └── tasks/            # 异步任务
│   │       ├── __init__.py
│   │       └── ai_analysis.py
│   ├── requirements.txt      # Python依赖
│   ├── Dockerfile           # Docker配置
│   └── .env.example         # 环境变量示例
├── frontend/                # 前端管理界面
│   ├── src/
│   │   ├── main.ts          # 应用入口
│   │   ├── App.vue          # 根组件
│   │   ├── components/      # 通用组件
│   │   │   ├── common/      # 基础组件
│   │   │   ├── charts/      # 图表组件
│   │   │   └── performance/ # 性能相关组件
│   │   ├── views/           # 页面组件
│   │   │   ├── Dashboard.vue    # 仪表板
│   │   │   ├── ProjectList.vue  # 项目列表
│   │   │   ├── PerformanceMonitor.vue # 性能监控
│   │   │   └── AnalysisResults.vue    # 分析结果
│   │   ├── router/          # 路由配置
│   │   │   └── index.ts
│   │   ├── store/           # 状态管理
│   │   │   ├── index.ts
│   │   │   ├── modules/
│   │   │   │   ├── project.ts
│   │   │   │   └── performance.ts
│   │   ├── api/             # API接口
│   │   │   ├── index.ts
│   │   │   ├── project.ts
│   │   │   └── performance.ts
│   │   ├── utils/           # 工具函数
│   │   │   ├── request.ts   # HTTP请求
│   │   │   └── format.ts    # 格式化工具
│   │   └── types/           # TypeScript类型定义
│   │       ├── project.ts
│   │       └── performance.ts
│   ├── package.json         # Node.js依赖
│   ├── vite.config.ts       # Vite配置
│   ├── tsconfig.json        # TypeScript配置
│   └── Dockerfile           # Docker配置
├── sdk/                     # 性能分析SDK
│   ├── performance_monitor/
│   │   ├── __init__.py
│   │   ├── core/            # 核心功能
│   │   │   ├── __init__.py
│   │   │   ├── collector.py # 数据收集器
│   │   │   ├── profiler.py  # 性能分析器
│   │   │   └── sender.py    # 数据发送器
│   │   ├── flask/           # Flask集成
│   │   │   ├── __init__.py
│   │   │   ├── middleware.py
│   │   │   └── decorators.py
│   │   ├── django/          # Django集成
│   │   │   ├── __init__.py
│   │   │   ├── middleware.py
│   │   │   └── decorators.py
│   │   ├── fastapi/         # FastAPI集成
│   │   │   ├── __init__.py
│   │   │   └── middleware.py
│   │   └── utils/           # 工具类
│   │       ├── __init__.py
│   │       ├── config.py    # 配置管理
│   │       └── logger.py    # 日志管理
│   ├── setup.py             # 安装配置
│   ├── requirements.txt     # 依赖
│   └── README.md           # 使用说明
├── docker-compose.yml       # Docker编排
├── README.md               # 项目说明
└── docs/                   # 文档
    ├── api.md              # API文档
    ├── installation.md     # 安装指南
    └── integration.md      # 集成指南
```

---

## 8. 部署配置

### 8.1 Docker Compose配置

```yaml
version: '3.8'

services:
  # MongoDB数据库
  mongodb:
    image: mongo:6.0
    container_name: pystrument-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD:-admin123}
      MONGO_INITDB_DATABASE: pystrument
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./backend/scripts/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js:ro
    networks:
      - pystrument-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: pystrument-redis
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis123}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - pystrument-network

  # 后端API服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: pystrument-backend
    environment:
      - MONGODB_URL=mongodb://admin:${MONGODB_PASSWORD:-admin123}@mongodb:27017/pystrument?authSource=admin
      - REDIS_URL=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=${DEBUG:-false}
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./backend:/app
    networks:
      - pystrument-network
    restart: unless-stopped

  # Celery任务队列
  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: pystrument-celery
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - MONGODB_URL=mongodb://admin:${MONGODB_PASSWORD:-admin123}@mongodb:27017/pystrument?authSource=admin
      - REDIS_URL=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - mongodb
      - redis
    volumes:
      - ./backend:/app
    networks:
      - pystrument-network
    restart: unless-stopped

  # 前端Web界面
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: pystrument-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - pystrument-network
    restart: unless-stopped

volumes:
  mongodb_data:
  redis_data:

networks:
  pystrument-network:
    driver: bridge
```

### 8.2 环境配置文件

#### 后端环境变量(.env)
```bash
# 数据库配置
MONGODB_URL=mongodb://admin:admin123@localhost:27017/pystrument?authSource=admin
REDIS_URL=redis://:redis123@localhost:6379/0

# 应用配置
DEBUG=true
SECRET_KEY=your-secret-key-here
API_VERSION=v1

# AI服务配置
OPENAI_API_KEY=your-openai-api-key
AI_SERVICE_TIMEOUT=30

# 监控配置
DEFAULT_SAMPLING_RATE=0.3
MAX_BATCH_SIZE=100
ASYNC_SEND_TIMEOUT=5

# 安全配置
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MAX_REQUEST_SIZE=10485760  # 10MB

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/pystrument/app.log
```

#### 前端环境变量(.env)
```bash
# API配置
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws

# 应用配置
VITE_APP_TITLE=性能分析平台
VITE_APP_VERSION=1.0.0

# 开发配置
VITE_DEV_PROXY=true
VITE_DEV_PORT=3000
```

---

## 9. AI分析服务

### 9.1 AI服务配置
```python
# AI服务配置示例
{
    "ai_services": {
        "openai": {
            "provider": "openai",
            "api_key": "${OPENAI_API_KEY}",
            "model": "gpt-4",
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 4000,
            "temperature": 0.3
        },
        "custom_service": {
            "provider": "custom",
            "endpoint": "http://your-ai-service.com/analyze",
            "headers": {
                "Authorization": "Bearer ${CUSTOM_AI_TOKEN}"
            },
            "timeout": 30
        }
    },
    "default_service": "openai",
    "analysis_templates": {
        "performance_analysis": "分析以下性能数据，识别瓶颈并提供优化建议...",
        "bottleneck_detection": "识别以下调用链路中的性能瓶颈..."
    }
}
```

### 9.2 AI分析工作流
```mermaid
graph TD
    A[用户点击深度分析] --> B[提取性能数据]
    B --> C[数据预处理]
    C --> D[调用AI服务]
    D --> E[解析AI响应]
    E --> F[生成结构化建议]
    F --> G[存储分析结果]
    G --> H[返回分析报告]
```

---

## 10. Celery任务队列

### 10.1 Celery架构设计

本项目使用Celery作为异步任务队列，处理耗时的AI分析任务，避免阻塞API响应。Celery架构包括：

- **任务生产者**: FastAPI后端服务，负责创建和分发任务
- **消息代理**: Redis，用于存储任务队列
- **任务工作者**: Celery Worker，执行实际的AI分析任务
- **结果存储**: Redis，存储任务执行结果

### 10.2 任务类型

#### 10.2.1 性能分析任务
```python
@celery_app.task(bind=True, name='ai_analysis.analyze_performance')
def analyze_performance_task(
    self,
    performance_record_id: str,
    ai_service: Optional[str] = None,
    priority: str = 'normal',
    analysis_id: Optional[str] = None
):
    """
    异步分析性能数据
    
    Args:
        performance_record_id: 性能记录ID
        ai_service: AI服务名称
        priority: 分析优先级
        analysis_id: 分析ID（可选，由API传入）
    """
```

#### 10.2.2 批量分析任务
```python
@celery_app.task(name='ai_analysis.batch_analyze_performance')
def batch_analyze_performance_task(
    performance_record_ids: list,
    ai_service: Optional[str] = None,
    priority: str = 'normal'
):
    """
    批量分析性能数据
    """
```

#### 10.2.3 数据清理任务
```python
@celery_app.task(name='ai_analysis.cleanup_old_analysis')
def cleanup_old_analysis_task(days: int = 30):
    """
    清理旧的分析记录
    
    Args:
        days: 保留天数
    """
```

#### 10.2.4 性能报告任务
```python
@celery_app.task(name='ai_analysis.performance_report')
def generate_performance_report_task(
    project_key: str,
    start_date: str,
    end_date: str,
    report_type: str = 'summary'
):
    """
    生成性能报告
    """
```

### 10.3 任务队列配置

#### 10.3.1 队列划分
```python
# 任务路由配置
celery_app.conf.task_routes = {
    'ai_analysis.analyze_performance': {'queue': 'analysis'},
    'ai_analysis.batch_analyze_performance': {'queue': 'batch'},
    'ai_analysis.cleanup_old_analysis': {'queue': 'maintenance'},
    'ai_analysis.performance_report': {'queue': 'reports'},
}
```

#### 10.3.2 定时任务
```python
# 定时任务配置
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-old-analysis': {
        'task': 'ai_analysis.cleanup_old_analysis',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点执行
        'args': (30,)  # 保留30天的数据
    },
}
```

### 10.4 启动和管理

#### 10.4.1 启动Celery Worker
```bash
# 使用脚本启动
./backend/start_celery.sh

# 或直接使用命令启动
cd backend
celery -A app.tasks.ai_analysis.celery_app worker \
  --loglevel=info \
  --concurrency=2 \
  -Q analysis,batch,maintenance,reports
```

#### 10.4.2 启动Celery Beat（定时任务）
```bash
# 启动定时任务调度器
cd backend
celery -A app.tasks.ai_analysis.celery_app beat --loglevel=info
```

#### 10.4.3 监控Celery任务
```bash
# 启动Flower监控工具
cd backend
celery -A app.tasks flower --port=5555
```

### 10.5 Docker部署配置

#### 10.5.1 docker-compose.yml配置
```yaml
# Celery任务队列
celery:
  build:
    context: ./backend
    dockerfile: Dockerfile
  container_name: pystrument-celery
  command: celery -A app.tasks.ai_analysis.celery_app worker --loglevel=info --concurrency=2 -Q analysis,batch,maintenance,reports
  environment:
    # 数据库配置
    - MONGODB_URL=mongodb://admin:${MONGODB_PASSWORD:-admin123}@mongodb:27017/pystrument?authSource=admin
    - REDIS_URL=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/0
    
    # AI服务配置
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - AI_SERVICE_TIMEOUT=30
    
    # Celery配置
    - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/1
    - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/2
    
    # 日志配置
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
    - LOG_FILE=/var/log/pystrument/celery.log
  depends_on:
    - mongodb
    - redis
  volumes:
    - ./backend:/app
    - celery_logs:/var/log/pystrument
  networks:
    - pystrument-network
  restart: unless-stopped

# Celery监控 (可选)
flower:
  build:
    context: ./backend
    dockerfile: Dockerfile
  container_name: pystrument-flower
  command: celery -A app.tasks flower --port=5555
  environment:
    - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/1
    - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/2
  ports:
    - "5555:5555"
  depends_on:
    - redis
    - celery
  networks:
    - pystrument-network
  restart: unless-stopped
  profiles:
    - monitoring
```

### 10.6 任务监控和调试

#### 10.6.1 查看任务状态
```bash
# 查看Celery Worker状态
celery -A app.tasks.ai_analysis.celery_app inspect active

# 查看任务统计
celery -A app.tasks.ai_analysis.celery_app inspect stats

# 查看任务队列
celery -A app.tasks.ai_analysis.celery_app inspect scheduled
```

#### 10.6.2 日志查看
```bash
# 查看Celery日志
tail -f /var/log/pystrument/celery.log

# 或在Docker环境中
docker-compose logs -f celery
```

### 10.7 性能调优

#### 10.7.1 并发配置
```bash
# 调整并发数
celery -A app.tasks.ai_analysis.celery_app worker --concurrency=4

# 预取乘数设置
celery -A app.tasks.ai_analysis.celery_app worker --prefetch-multiplier=1
```

#### 10.7.2 内存管理
```python
# Celery配置优化
celery_app.conf.update(
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_time_limit=300,  # 5分钟超时
)
```

---

## 11. 测试与质量保证

### 11.1 运行测试

```bash
# 安装测试依赖
./run_tests.sh install-deps

# 运行单元测试
./run_tests.sh unit

# 运行集成测试
./run_tests.sh integration

# 运行端到端测试
./run_tests.sh e2e

# 运行所有测试
./run_tests.sh all

# 生成覆盖率报告
./run_tests.sh coverage
```

### 11.2 代码质量检查

```bash
# 运行代码质量检查
./run_tests.sh quality
```

---

## 12. 故障排除

### 12.1 常见问题

1. **连接数据库失败**
   ```bash
   # 检查MongoDB连接
   docker-compose logs mongodb
   
   # 测试连接
   mongo mongodb://localhost:27017/performance
   ```

2. **性能数据未收集**
   ```python
   # 检查采样率配置
   config.sampling_rate = 100.0  # 设置为100%用于调试
   
   # 检查项目键是否正确
   config.project_key = "your_correct_project_key"
   ```

3. **AI分析失败**
   ```bash
   # 检查Celery任务状态
   docker-compose logs celery
   
   # 检查AI服务配置
   curl http://localhost:8000/api/v1/analysis/config/ai-services
   ```

### 12.2 日志调试

```python
# 启用调试日志
import logging
logging.getLogger('performance_monitor').setLevel(logging.DEBUG)
```

---

## 13. 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 14. 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 15. 联系我们

- 项目地址: https://github.com/your-org/pystrument
- 问题反馈: https://github.com/your-org/pystrument/issues
- 邮箱: dev@performance-monitor.com

## 16. 更新日志

### v1.0.0 (2024-08-24)
- 初始版本发布
- 支持Flask应用接入
- 基础性能监控功能
- AI分析功能
- Vue3管理界面

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！