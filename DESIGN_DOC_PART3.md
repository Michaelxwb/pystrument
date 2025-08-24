## 4.4 性能分析SDK - 第三方应用接入方案详细设计

### 4.4.1 接入方式概览

| 接入方式 | 适用场景 | 集成难度 | 性能影响 | 代码侵入性 | 推荐指数 |
|----------|----------|----------|----------|------------|----------|
| 中间件方式 | Web框架全局监控 | 低 | 低 | 最小 | ⭐⭐⭐⭐⭐ |
| 装饰器方式 | 函数级精确监控 | 中 | 最小 | 中 | ⭐⭐⭐⭐ |
| WSGI包装器 | Flask应用快速接入 | 低 | 低 | 无 | ⭐⭐⭐⭐⭐ |
| 配置文件接入 | 零代码修改 | 最低 | 低 | 无 | ⭐⭐⭐⭐⭐ |
| 手动埋点 | 自定义监控点 | 高 | 可控 | 高 | ⭐⭐⭐ |

### 4.4.2 Flask应用接入方案

#### 方案1: WSGI包装器（推荐）
```python
# 最简单的接入方式，无需修改任何业务代码
# app.py
from flask import Flask
from performance_monitor.flask import PerformanceWSGIWrapper

app = Flask(__name__)

# 原有的路由定义保持不变
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    # 业务逻辑完全不需要修改
    user = User.query.get(user_id)
    return jsonify(user.to_dict())

if __name__ == '__main__':
    # 只需要用包装器包装原有的app
    wrapped_app = PerformanceWSGIWrapper(
        app, 
        project_key="your_project_key",
        api_endpoint="http://platform.example.com/api"
    )
    wrapped_app.run(debug=True)
```

#### 方案2: 配置文件接入（零代码修改）
```yaml
# performance_config.yaml
performance_monitor:
  enabled: true
  project_key: "your_project_key"
  api_endpoint: "http://platform.example.com/api"
  
  # 监控范围配置
  monitoring:
    include_patterns:
      - "/api/*"           # 监控所有API接口
      - "/admin/*"         # 监控管理接口
    exclude_patterns:
      - "/health"          # 排除健康检查
      - "/static/*"        # 排除静态资源
      - "*.css"
      - "*.js"
    
    # 采样配置
    sampling_rate: 0.3     # 30%采样率
    error_sampling: 1.0    # 错误请求100%采样
    slow_threshold: 1.0    # 慢请求阈值1秒
    slow_sampling: 1.0     # 慢请求100%采样
  
  # 数据传输配置
  transport:
    async_send: true       # 异步发送数据
    batch_size: 50         # 批量发送大小
    retry_times: 3         # 重试次数
```

```python
# 使用环境变量启动应用，无需修改代码
# 在启动脚本中设置环境变量
export PERFORMANCE_MONITOR_CONFIG="/path/to/performance_config.yaml"
export FLASK_APP="app.py"
flask run

# 或者通过Python脚本自动加载配置
# run_with_monitor.py
import os
from performance_monitor.auto_loader import auto_instrument
from your_app import app

# 自动加载配置并启动监控
auto_instrument(app, config_file="performance_config.yaml")

if __name__ == '__main__':
    app.run()
```

#### 方案3: 中间件接入
```python
# app.py
from flask import Flask
from performance_monitor.flask import PerformanceMiddleware

app = Flask(__name__)

# 配置性能监控中间件
app.wsgi_app = PerformanceMiddleware(
    app.wsgi_app,
    config={
        'project_key': 'your_project_key',
        'api_endpoint': 'http://platform.example.com/api',
        'sampling_rate': 0.3,
        'exclude_paths': ['/health', '/metrics'],
        'track_sql': True,
        'track_templates': True
    }
)

# 业务代码保持不变
@app.route('/api/users')
def list_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])
```

### 4.4.3 Django应用接入方案

#### 方案1: 中间件接入（推荐）
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

#### 方案2: 装饰器接入
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

### 4.4.4 FastAPI应用接入方案

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

### 4.4.5 SDK安装和快速开始指南

#### 安装方式
```bash
# 通过pip安装
pip install performance-monitor-sdk

# 或者通过requirements.txt
echo "performance-monitor-sdk>=1.0.0" >> requirements.txt
pip install -r requirements.txt
```

#### 快速开始示例
```python
# 1. 获取项目密钥（通过Web管理界面或API）
# 访问: http://platform.example.com/dashboard
# 创建新项目，获取project_key

# 2. 最简单的Flask接入
from flask import Flask
from performance_monitor import auto_monitor

app = Flask(__name__)

# 一行代码启用监控
auto_monitor(app, project_key="your_project_key")

@app.route('/api/test')
def test_api():
    return {'message': 'Hello World'}

if __name__ == '__main__':
    app.run()
```

### 4.4.6 高级配置选项

#### 环境变量配置
```bash
# .env 文件
PERFORMANCE_MONITOR_PROJECT_KEY=your_project_key
PERFORMANCE_MONITOR_API_ENDPOINT=http://platform.example.com/api
PERFORMANCE_MONITOR_ENABLED=true
PERFORMANCE_MONITOR_SAMPLING_RATE=0.3
PERFORMANCE_MONITOR_ASYNC_SEND=true
PERFORMANCE_MONITOR_LOG_LEVEL=INFO
```

#### 详细配置文件
```yaml
# performance_config.yaml
performance_monitor:
  project_key: "${PERFORMANCE_MONITOR_PROJECT_KEY}"
  api_endpoint: "${PERFORMANCE_MONITOR_API_ENDPOINT}"
  enabled: true
  
  # 采样配置
  sampling:
    rate: 0.3                    # 基础采样率
    error_rate: 1.0              # 错误请求100%采样
    slow_request_threshold: 1.0   # 慢请求阈值（秒）
    slow_request_rate: 1.0       # 慢请求100%采样
  
  # 过滤配置
  filters:
    exclude_paths:
      - "/health"
      - "/metrics"
      - "/static/*"
    include_patterns:
      - "/api/*"
      - "/admin/*"
    max_request_size: 10485760   # 10MB
    max_response_size: 10485760  # 10MB
  
  # 监控项配置
  tracking:
    sql_queries: true
    external_requests: true
    cache_operations: true
    memory_usage: true
    template_rendering: true
```