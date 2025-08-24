# 基于Pyinstrument的性能分析平台

## 项目概述

这是一个基于pyinstrument的性能分析平台，提供插件式的快速接入方案，支持自动监控全平台接口性能，记录函数级执行链路，并集成AI工具进行自动化性能分析和优化建议。

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
- **AI集成**: 支持OpenAI API、自定义AI服务

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

## 快速开始

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

## SDK使用指南

### Flask应用接入

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

### 配置文件

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

## API接口文档

### 项目管理

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

### 性能数据

```bash
# 提交性能数据
POST /api/v1/performance/collect

# 查询性能记录
GET /api/v1/performance/records?project_key={key}&page=1&size=20

# 获取性能趋势
GET /api/v1/performance/trends/{project_key}?time_range=24h
```

### AI分析

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

## 测试

### 运行测试

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

### 代码质量检查

```bash
# 运行代码质量检查
./run_tests.sh quality
```

## 部署指南

### 生产环境部署

1. **准备环境**
   ```bash
   # 复制生产配置
   cp docker-compose.prod.yml docker-compose.yml
   
   # 设置环境变量
   export MONGODB_URL="mongodb://prod-mongo:27017/performance"
   export REDIS_URL="redis://prod-redis:6379/0"
   export SECRET_KEY="your-secret-key"
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **初始化数据库**
   ```bash
   docker-compose exec backend python -m app.scripts.init_db
   ```

### 监控和日志

- **应用监控**: 使用Prometheus + Grafana
- **日志收集**: 使用ELK Stack
- **健康检查**: http://your-domain/health

## 性能优化建议

### 后端优化

1. **数据库索引**
   ```python
   # MongoDB索引建议
   db.performance_records.create_index([("project_key", 1), ("timestamp", -1)])
   db.performance_records.create_index([("trace_id", 1)])
   ```

2. **缓存策略**
   ```python
   # Redis缓存配置
   CACHE_CONFIG = {
       "project_stats": 300,  # 5分钟
       "performance_trends": 600,  # 10分钟
   }
   ```

### 前端优化

1. **懒加载**: 大数据列表使用虚拟滚动
2. **缓存**: 使用Pinia持久化存储
3. **CDN**: 静态资源使用CDN加速

## 故障排除

### 常见问题

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

### 日志调试

```python
# 启用调试日志
import logging
logging.getLogger('performance_monitor').setLevel(logging.DEBUG)
```

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系我们

- 项目地址: https://github.com/your-org/pystrument
- 问题反馈: https://github.com/your-org/pystrument/issues
- 邮箱: dev@performance-monitor.com

## 更新日志

### v1.0.0 (2024-08-24)
- 初始版本发布
- 支持Flask应用接入
- 基础性能监控功能
- AI分析功能
- Vue3管理界面

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！