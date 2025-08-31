# 性能分析平台最终文档

## 项目概述

这是一个基于 [pyinstrument](https://github.com/joerick/pyinstrument) 的性能分析平台，提供插件式的快速接入方案，支持自动监控全平台接口性能，记录函数级执行链路，并集成AI工具进行自动化性能分析和优化建议。

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

## 部署指南

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

## SDK使用指南

### SDK构建步骤

#### 1. 构建SDK包

```bash
# 进入SDK目录
cd /Users/jahan/workspace/pystrument/sdk

# 清理之前的构建产物
rm -rf build dist *.egg-info

# 构建SDK包
python3 setup.py sdist bdist_wheel
```

构建完成后，会在`dist`目录下生成两个文件：
- `performance_monitor_sdk-1.0.0-py3-none-any.whl` (wheel包)
- `performance_monitor_sdk-1.0.0.tar.gz` (源码包)

#### 2. 安装SDK

##### 本地安装
```bash
# 安装wheel包
python3 -m pip install dist/performance_monitor_sdk-1.0.0-py3-none-any.whl

# 或者强制重新安装
python3 -m pip install --force-reinstall dist/performance_monitor_sdk-1.0.0-py3-none-any.whl
```

##### 框架特定安装
```bash
# 安装支持特定框架的SDK
pip install performance-monitor-sdk[flask]     # Flask支持
pip install performance-monitor-sdk[django]    # Django支持
pip install performance-monitor-sdk[fastapi]   # FastAPI支持
```

#### 3. SDK目录结构

```
sdk/
├── performance_monitor/           # SDK主目录
│   ├── __init__.py               # 主入口模块
│   ├── core/                     # 核心功能模块
│   │   ├── collector.py          # 性能数据收集器
│   │   ├── profiler.py           # 性能分析器管理器
│   │   └── sender.py             # 数据发送器
│   ├── utils/                    # 工具模块
│   │   ├── config.py             # 配置管理
│   │   └── decorator.py          # 装饰器工具
│   ├── flask/                    # Flask集成模块
│   │   ├── __init__.py
│   │   ├── middleware.py         # 中间件
│   │   └── decorators.py         # 装饰器
│   ├── django/                   # Django集成模块
│   │   └── __init__.py
│   └── fastapi/                  # FastAPI集成模块
│       └── __init__.py
├── setup.py                      # 构建配置文件
├── requirements.txt              # 依赖配置文件
└── MANIFEST.in                  # 包含文件配置
```

### SDK集成方式

#### 1. 中间件方式（推荐）

##### Flask应用
```python
from flask import Flask
from performance_monitor.flask import PerformanceMiddleware

app = Flask(__name__)

# 配置性能监控
config = {
    'project_key': 'your-project-key',
    'api_endpoint': 'http://localhost:8000/api/v1/performance/collect'
}

# 添加性能监控中间件
app.wsgi_app = PerformanceMiddleware(app.wsgi_app, config)
```

##### Django应用
```python
# 在settings.py中添加中间件
MIDDLEWARE = [
    'performance_monitor.django.PerformanceMiddleware',
    # ... 其他中间件
]

# 在settings.py中配置
PERFORMANCE_MONITOR = {
    'project_key': 'your-project-key',
    'api_endpoint': 'http://localhost:8000/api/v1/performance/collect'
}
```

##### FastAPI应用
```python
from fastapi import FastAPI
from performance_monitor.fastapi import PerformanceMiddleware

app = FastAPI()

# 添加性能监控中间件
app.add_middleware(PerformanceMiddleware, config={
    'project_key': 'your-project-key',
    'api_endpoint': 'http://localhost:8000/api/v1/performance/collect'
})
```

#### 2. 装饰器方式

```python
from performance_monitor import monitor_performance

@monitor_performance(project_key='your-project-key', api_endpoint='http://localhost:8000/api/v1/performance/collect')
def your_function():
    # 你的业务逻辑
    pass
```

#### 3. 手动方式

```python
from performance_monitor import Config, PerformanceCollector

# 创建配置
config = Config(
    project_key='your-project-key',
    api_endpoint='http://localhost:8000/api/v1/performance/collect'
)

# 创建性能收集器
collector = PerformanceCollector(config)

# 手动收集性能数据
with collector.collect():
    # 你的业务逻辑
    pass
```

### SDK配置方式

#### 1. 代码中直接配置
```python
from performance_monitor import Config

config = Config(
    project_key='your-project-key',
    api_endpoint='http://localhost:8000/api/v1/performance/collect',
    sampling_rate=0.5,  # 采样率50%
    batch_size=100,     # 批量发送大小
    async_send=True     # 异步发送
)
```

#### 2. 环境变量配置
```bash
export PERFORMANCE_MONITOR_PROJECT_KEY=your-project-key
export PERFORMANCE_MONITOR_API_ENDPOINT=http://localhost:8000/api/v1/performance/collect
export PERFORMANCE_MONITOR_SAMPLING_RATE=0.5
export PERFORMANCE_MONITOR_BATCH_SIZE=100
```

#### 3. YAML配置文件
```yaml
performance_monitor:
  project_key: your-project-key
  api_endpoint: http://localhost:8000/api/v1/performance/collect
  sampling_rate: 0.5
  batch_size: 100
  async_send: true
```

#### 4. JSON配置文件
```json
{
  "performance_monitor": {
    "project_key": "your-project-key",
    "api_endpoint": "http://localhost:8000/api/v1/performance/collect",
    "sampling_rate": 0.5,
    "batch_size": 100,
    "async_send": true
  }
}
```

## API接口说明

### 性能数据收集接口
- **URL**: `/api/v1/performance/collect`
- **方法**: POST
- **描述**: 收集性能数据

### 性能数据批量收集接口
- **URL**: `/api/v1/performance/batch`
- **方法**: POST
- **描述**: 批量收集性能数据

### AI分析接口
- **URL**: `/api/v1/analysis/analyze/{performance_record_id}`
- **方法**: POST
- **描述**: 触发AI性能分析

## 故障排除

### 常见问题

1. **SDK导入失败**
   - 确保SDK已正确安装
   - 检查Python环境路径

2. **性能数据未上报**
   - 检查项目密钥是否正确
   - 检查API端点是否可达
   - 查看SDK日志输出

3. **AI分析失败**
   - 检查AI服务配置
   - 确认网络连接正常
   - 查看Celery任务日志

### 日志查看

```bash
# 查看后端服务日志
docker-compose logs backend

# 查看Celery服务日志
docker-compose logs celery

# 查看前端服务日志
docker-compose logs frontend
```

## 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。