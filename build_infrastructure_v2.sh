#!/bin/bash

# 阿里云镜像仓库基础设施镜像构建和推送脚本 V2.0
# 镜像仓库: crpi-x3k4zm1fio56r4y0.cn-shenzhen.personal.cr.aliyuncs.com/xwbclound_hub

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 镜像仓库配置
REGISTRY="crpi-x3k4zm1fio56r4y0.cn-shenzhen.personal.cr.aliyuncs.com"
NAMESPACE="xwbclound_hub"
VERSION="v2.0"

# 基础设施镜像名称
MONGO_IMAGE="${REGISTRY}/${NAMESPACE}/pystrument-mongo:${VERSION}"
REDIS_IMAGE="${REGISTRY}/${NAMESPACE}/pystrument-redis:${VERSION}"
NGINX_IMAGE="${REGISTRY}/${NAMESPACE}/pystrument-nginx:${VERSION}"

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 登录阿里云镜像仓库
login_registry() {
    print_info "登录阿里云镜像仓库..."
    docker login ${REGISTRY}
    if [ $? -ne 0 ]; then
        print_error "登录失败，请检查用户名和密码"
        exit 1
    fi
    print_success "登录成功"
}

# 构建MongoDB镜像
build_mongo() {
    print_info "构建MongoDB镜像..."
    
    # 创建临时Dockerfile目录
    mkdir -p /tmp/pystrument-mongo
    
    cat > /tmp/pystrument-mongo/Dockerfile << 'EOF'
FROM mongo:7.0

LABEL maintainer="xwbclound"
LABEL version="v2.0"
LABEL description="Pystrument MongoDB with custom initialization"

# 设置工作目录
WORKDIR /docker-entrypoint-initdb.d

# 复制初始化脚本
COPY init-mongo.js /docker-entrypoint-initdb.d/

# 设置权限
RUN chmod +x /docker-entrypoint-initdb.d/init-mongo.js

# 暴露端口
EXPOSE 27017

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD mongosh --eval "db.adminCommand('ping')" || exit 1

# 启动命令
CMD ["mongod", "--auth", "--bind_ip_all"]
EOF

    # 复制初始化脚本
    cp /root/security/pystrument/scripts/init-mongo.js /tmp/pystrument-mongo/
    
    # 构建镜像
    docker build -t ${MONGO_IMAGE} /tmp/pystrument-mongo/
    
    # 清理临时目录
    rm -rf /tmp/pystrument-mongo
    
    print_success "MongoDB镜像构建完成: ${MONGO_IMAGE}"
}

# 构建Redis镜像
build_redis() {
    print_info "构建Redis镜像..."
    
    # 创建临时Dockerfile目录
    mkdir -p /tmp/pystrument-redis
    
    cat > /tmp/pystrument-redis/Dockerfile << 'EOF'
FROM redis:7-alpine

LABEL maintainer="xwbclound"
LABEL version="v2.0"
LABEL description="Pystrument Redis with persistence and security"

# 安装redis-cli工具
RUN apk add --no-cache redis

# 创建配置目录和数据目录
RUN mkdir -p /usr/local/etc/redis /data && \
    chown -R redis:redis /data

# 创建Redis配置
RUN echo "# Redis配置" > /usr/local/etc/redis/redis.conf && \
    echo "bind 0.0.0.0" >> /usr/local/etc/redis/redis.conf && \
    echo "port 6379" >> /usr/local/etc/redis/redis.conf && \
    echo "timeout 300" >> /usr/local/etc/redis/redis.conf && \
    echo "tcp-keepalive 300" >> /usr/local/etc/redis/redis.conf && \
    echo "loglevel notice" >> /usr/local/etc/redis/redis.conf && \
    echo "databases 16" >> /usr/local/etc/redis/redis.conf && \
    echo "save 900 1" >> /usr/local/etc/redis/redis.conf && \
    echo "save 300 10" >> /usr/local/etc/redis/redis.conf && \
    echo "save 60 10000" >> /usr/local/etc/redis/redis.conf && \
    echo "rdbcompression yes" >> /usr/local/etc/redis/redis.conf && \
    echo "rdbchecksum yes" >> /usr/local/etc/redis/redis.conf && \
    echo "dbfilename dump.rdb" >> /usr/local/etc/redis/redis.conf && \
    echo "dir /data" >> /usr/local/etc/redis/redis.conf && \
    echo "appendonly yes" >> /usr/local/etc/redis/redis.conf && \
    echo "appendfilename appendonly.aof" >> /usr/local/etc/redis/redis.conf && \
    echo "appendfsync everysec" >> /usr/local/etc/redis/redis.conf && \
    echo "maxmemory 256mb" >> /usr/local/etc/redis/redis.conf && \
    echo "maxmemory-policy allkeys-lru" >> /usr/local/etc/redis/redis.conf

# 暴露端口
EXPOSE 6379

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD redis-cli ping || exit 1

# 启动命令
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]
EOF

    # 构建镜像
    docker build -t ${REDIS_IMAGE} /tmp/pystrument-redis/
    
    # 清理临时目录
    rm -rf /tmp/pystrument-redis
    
    print_success "Redis镜像构建完成: ${REDIS_IMAGE}"
}

# 构建Nginx镜像
build_nginx() {
    print_info "构建Nginx镜像..."
    
    # 创建临时Dockerfile目录
    mkdir -p /tmp/pystrument-nginx
    
    cat > /tmp/pystrument-nginx/Dockerfile << 'EOF'
FROM nginx:alpine

LABEL maintainer="xwbclound"
LABEL version="v2.0"
LABEL description="Pystrument Nginx with custom configuration"

# 安装必要的工具
RUN apk add --no-cache curl

# 复制配置文件
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# 创建日志目录
RUN mkdir -p /var/log/nginx && \
    touch /var/log/nginx/access.log && \
    touch /var/log/nginx/error.log

# 创建SSL目录
RUN mkdir -p /etc/nginx/ssl

# 设置权限
RUN chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# 暴露端口
EXPOSE 80 443

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# 启动命令
CMD ["nginx", "-g", "daemon off;"]
EOF

    # 复制Nginx配置
    cp -r /root/security/pystrument/nginx/ /tmp/pystrument-nginx/
    
    # 构建镜像
    docker build -t ${NGINX_IMAGE} /tmp/pystrument-nginx/
    
    # 清理临时目录
    rm -rf /tmp/pystrument-nginx
    
    print_success "Nginx镜像构建完成: ${NGINX_IMAGE}"
}

# 推送镜像
push_images() {
    print_info "开始推送基础设施镜像到阿里云仓库..."
    
    print_info "推送MongoDB镜像..."
    docker push ${MONGO_IMAGE}
    print_success "MongoDB镜像推送完成"
    
    print_info "推送Redis镜像..."
    docker push ${REDIS_IMAGE}
    print_success "Redis镜像推送完成"
    
    print_info "推送Nginx镜像..."
    docker push ${NGINX_IMAGE}
    print_success "Nginx镜像推送完成"
}

# 验证镜像
verify_images() {
    print_info "验证镜像上传成功..."
    
    docker pull ${MONGO_IMAGE}
    docker pull ${REDIS_IMAGE}
    docker pull ${NGINX_IMAGE}
    
    print_success "所有基础设施镜像验证通过"
}

# 显示镜像信息
show_images() {
    print_info "基础设施镜像信息汇总:"
    echo "MongoDB镜像: ${MONGO_IMAGE}"
    echo "Redis镜像: ${REDIS_IMAGE}"
    echo "Nginx镜像: ${NGINX_IMAGE}"
    echo ""
    echo "使用示例:"
    echo "docker pull ${MONGO_IMAGE}"
    echo "docker pull ${REDIS_IMAGE}"
    echo "docker pull ${NGINX_IMAGE}"
}

# 主函数
main() {
    print_info "开始构建并推送V2.0版本基础设施镜像到阿里云仓库"
    print_info "镜像仓库: ${REGISTRY}/${NAMESPACE}"
    print_info "版本: ${VERSION}"
    echo ""
    
    # 检查Docker是否安装
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 执行构建和推送流程
    login_registry
    build_mongo
    build_redis
    build_nginx
    push_images
    verify_images
    show_images
    
    print_success "所有基础设施镜像构建和推送完成！"
}

# 执行主函数
main "$@"