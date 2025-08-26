# Performance Monitor SDK

基于pyinstrument的性能分析和监控SDK。

## 功能特性

- 支持Flask、Django、FastAPI等Web框架
- 提供中间件、WSGI包装器、装饰器等多种接入方式
- 函数级性能分析和调用链记录
- 支持配置文件和环境变量配置

## 安装方式

```bash
pip install performance-monitor-sdk
```

## 使用方法

```python
from flask import Flask
from performance_monitor.flask import FlaskMiddleware

app = Flask(__name__)
FlaskMiddleware(app, 
    project_key="your_project_key", 
    api_endpoint="http://your-performance-platform.com/api/v1/collect"
)
```