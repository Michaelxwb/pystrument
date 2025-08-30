# 基于Pyinstrument的性能分析平台

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.x-brightgreen.svg)](https://vuejs.org/)

这是一个基于 [pyinstrument](https://github.com/joerick/pyinstrument) 的性能分析平台，提供插件式的快速接入方案，支持自动监控全平台接口性能，记录函数级执行链路，并集成AI工具进行自动化性能分析和优化建议。

## 🌟 核心特性

- 🚀 **快速接入**: 支持Flask、Django、FastAPI等多种框架的零代码或最小代码接入
- 📊 **实时监控**: 自动监控接口性能，记录详细的函数调用链路
- 🤖 **AI分析**: 集成AI工具自动分析性能瓶颈，提供优化建议
- 📈 **可视化界面**: Vue3前端管理界面，支持性能数据可视化
- 🔄 **历史版本管理**: 支持查看历史版本的接口性能数据对比
- 🛡️ **插件式设计**: 不影响目标项目的正常功能

## 🏗️ 技术架构

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

## 🚀 快速开始

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

# 访问前端界面
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

## 📖 使用指南

### 1. 创建项目
在前端界面或通过API创建一个新的监控项目，获取项目密钥。

### 2. 集成SDK
在目标项目中集成Python SDK：

```python
from performance_monitor import PerformanceMonitor

# 初始化监控器
monitor = PerformanceMonitor(
    project_key="your-project-key",
    api_url="http://localhost:8000/api/v1/performance/collect"
)

# 在应用入口处启用监控
app = monitor.instrument_app(your_app)
```

### 3. 查看监控数据
访问前端界面查看实时性能数据和AI分析结果。

## 🤖 AI分析服务

平台支持多种AI服务提供商：
- OpenAI (GPT系列)
- 阿里云千问
- DeepSeek
- 自定义AI服务

可以在系统设置中配置AI服务参数。

## 📁 项目结构

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
├── sdk/               # Python SDK
├── docker-compose.yml # Docker编排文件
└── docs/              # 文档
```

## 🧪 测试

```bash
# 运行后端测试
cd backend
python -m pytest

# 运行端到端测试
./run_tests.sh
```

## 📄 许可证

本项目采用MIT许可证，详情请见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 联系方式

如有任何问题，请提交Issue或联系项目维护者。
