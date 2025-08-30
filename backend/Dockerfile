# 多阶段构建 - 基础镜像
FROM python:3.9.6-slim as base

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# 开发阶段
FROM base as development

# 安装开发依赖
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /var/log/pystrument && \
    chown -R appuser:appuser /var/log/pystrument

# 切换到应用用户
USER appuser

# 暴露端口
EXPOSE 8000

# 开发环境启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 生产阶段
FROM base as production

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /var/log/pystrument && \
    mkdir -p /app/tmp && \
    chown -R appuser:appuser /var/log/pystrument /app

# 切换到应用用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 生产环境启动命令
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-"]

# 默认使用生产阶段
FROM production