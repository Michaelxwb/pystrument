# 项目目录结构和部署配置

## 1. 完整项目目录结构

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

## 2. Docker Compose配置

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

## 3. 环境配置文件

### 3.1 后端环境变量(.env)
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

### 3.2 前端环境变量(.env)
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

## 4. 部署启动命令

### 4.1 开发环境启动
```bash
# 1. 启动基础服务
docker-compose up -d mongodb redis

# 2. 启动后端服务
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 启动Celery工作进程
celery -A app.tasks worker --loglevel=info

# 4. 启动前端服务
cd frontend
npm install
npm run dev
```

### 4.2 生产环境部署
```bash
# 1. 设置环境变量
export MONGODB_PASSWORD=your-strong-password
export REDIS_PASSWORD=your-redis-password
export OPENAI_API_KEY=your-openai-key

# 2. 启动所有服务
docker-compose up -d

# 3. 检查服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f backend
```

## 5. 监控和维护

### 5.1 健康检查
```bash
# 检查后端API健康状态
curl http://localhost:8000/health

# 检查前端服务
curl http://localhost:3000

# 检查数据库连接
docker exec pystrument-mongodb mongo --eval "db.adminCommand('ismaster')"
```

### 5.2 数据备份
```bash
# MongoDB数据备份
docker exec pystrument-mongodb mongodump --authenticationDatabase admin -u admin -p admin123 --out /backup

# Redis数据备份
docker exec pystrument-redis redis-cli --rdb /data/backup.rdb
```

## 6. SDK打包发布

### 6.1 SDK构建脚本
```bash
# 构建SDK包
cd sdk
python setup.py sdist bdist_wheel

# 本地安装测试
pip install dist/performance-monitor-sdk-1.0.0.tar.gz

# 发布到PyPI（可选）
twine upload dist/*
```

### 6.2 SDK安装验证
```python
# 验证SDK安装
import performance_monitor
print(performance_monitor.__version__)

# 快速测试
from performance_monitor import auto_monitor
print("SDK安装成功!")
```