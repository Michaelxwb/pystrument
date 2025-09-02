# iFlow CLI 项目上下文文档

## 项目概述

这是一个基于 **Pyinstrument** 的高性能分析平台，提供插件式的快速接入方案，支持自动监控全平台接口性能，记录函数级执行链路，并集成AI工具进行自动化性能分析和优化建议。

### 核心特性
- 🚀 **快速接入**: 支持Flask、Django、FastAPI等多种框架的零代码或最小代码接入
- 📊 **实时监控**: 自动监控接口性能，记录详细的函数调用链路
- 🤖 **AI分析**: 集成AI工具自动分析性能瓶颈，提供优化建议
- 📈 **可视化界面**: Vue3前端管理界面，支持性能数据可视化
- 🔄 **历史版本管理**: 支持查看历史版本的接口性能数据对比
- 🛡️ **插件式设计**: 不影响目标项目的正常功能

## 技术架构

### 后端技术栈
- **框架**: FastAPI (高性能异步Web框架)
- **数据库**: MongoDB (主数据库) + Redis (缓存)
- **性能分析**: pyinstrument
- **任务队列**: Celery + Redis
- **AI集成**: 支持OpenAI API、阿里云千问、DeepSeek、自定义AI服务

### 前端技术栈
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **图表可视化**: ECharts
- **构建工具**: Vite

### SDK组件
- **Python SDK**: 支持Flask、Django、FastAPI等Web框架
- **配置管理**: YAML/JSON配置文件
- **数据传输**: HTTP REST API

## 项目结构

```
pystrument/
├── backend/           # 后端服务
│   ├── app/           # 应用代码
│   │   ├── api/       # API路由
│   │   ├── services/  # 业务逻辑
│   │   ├── tasks/     # Celery任务
│   │   └── utils/     # 工具函数
│   ├── tests/         # 后端测试
│   └── requirements.txt
├── frontend/          # 前端界面
│   ├── src/           # 源代码
│   └── package.json
├── nginx/             # Nginx配置
│   ├── nginx.conf     # 主配置文件
│   └── conf.d/        # 站点配置目录
├── sdk/               # Python SDK
├── docker-compose.yml # Docker编排文件
└── docs/              # 文档
```

## 快速开始

### 环境要求
- Node.js v18+
- Python 3.9+
- Docker & Docker Compose (推荐)

### 使用Docker Compose部署 (推荐)

```bash
# 克隆项目
git clone <repository-url>
cd pystrument

# 启动所有服务
docker-compose up -d

# 访问前端界面 (通过Nginx)
# http://localhost

# 或者直接访问前端服务
# http://localhost:3000

# 访问API文档
# http://localhost:8000/docs
```

### 本地开发部署

#### 后端服务
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动MongoDB和Redis (需要单独安装)
# 或使用Docker启动数据库服务
docker-compose up -d mongodb redis

# 启动后端服务
python -m app.main

# 启动Celery任务队列
./start_celery.sh
```

#### 前端服务
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 开发命令

### 后端开发
```bash
# 运行测试
./run_tests.sh unit          # 单元测试
./run_tests.sh integration   # 集成测试
./run_tests.sh e2e          # 端到端测试
./run_tests.sh coverage     # 生成覆盖率报告
./run_tests.sh quality      # 代码质量检查

# 代码格式化
cd backend
black app/
isort app/
flake8 app/
```

### 前端开发
```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint
npm run type-check

# 格式化代码
npm run format
```

## SDK使用指南

### 安装SDK
```bash
# 构建SDK
cd sdk
python3 setup.py sdist bdist_wheel

# 安装SDK
pip install dist/performance_monitor_sdk-1.0.0-py3-none-any.whl
```

### 集成方式

#### Flask应用
```python
from flask import Flask
from performance_monitor.flask import PerformanceMiddleware

app = Flask(__name__)
app.wsgi_app = PerformanceMiddleware(app.wsgi_app, {
    'project_key': 'your-project-key',
    'api_endpoint': 'http://localhost:8000/api/v1/performance/collect'
})
```

#### Django应用
```python
# settings.py
MIDDLEWARE = [
    'performance_monitor.django.PerformanceMiddleware',
    # ... 其他中间件
]

PERFORMANCE_MONITOR = {
    'project_key': 'your-project-key',
    'api_endpoint': 'http://localhost:8000/api/v1/performance/collect'
}
```

#### FastAPI应用
```python
from fastapi import FastAPI
from performance_monitor.fastapi import PerformanceMiddleware

app = FastAPI()
app.add_middleware(PerformanceMiddleware, config={
    'project_key': 'your-project-key',
    'api_endpoint': 'http://localhost:8000/api/v1/performance/collect'
})
```

## 环境配置

### 环境变量

#### 后端配置
```bash
# 数据库
MONGODB_URL=mongodb://admin:password@mongodb:27017/pystrument?authSource=admin
REDIS_URL=redis://:password@redis:6379/0

# AI服务
OPENAI_API_KEY=your-openai-api-key

# 安全配置
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 日志
LOG_LEVEL=INFO
```

#### 前端配置
```bash
# 开发环境
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000/ws
VITE_APP_TITLE=性能分析平台
```

## API接口

### 主要接口
- **项目管理**: `/api/v1/projects`
- **性能数据**: `/api/v1/performance`
- **AI分析**: `/api/v1/analysis`
- **仪表盘**: `/api/v1/dashboard`
- **系统设置**: `/api/v1/settings`

### 健康检查
- **健康状态**: `GET /health`
- **API文档**: `GET /docs` (开发环境)

## 故障排除

### 常见问题
1. **端口冲突**: 检查8000、3000、27017、6379端口是否被占用
2. **权限问题**: 确保有Docker和文件系统权限
3. **依赖问题**: 使用`pip install -r requirements.txt`重新安装依赖

### 日志查看
```bash
# Docker日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs celery

# 本地日志
tail -f backend/logs/app.log
```

## 许可证

本项目采用MIT许可证，详情请见LICENSE文件。