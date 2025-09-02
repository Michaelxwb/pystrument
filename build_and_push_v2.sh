#!/bin/bash

# 阿里云镜像仓库构建和推送脚本 V2.0
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

# 镜像名称
BACKEND_IMAGE="${REGISTRY}/${NAMESPACE}/pystrument-backend:${VERSION}"
FRONTEND_IMAGE="${REGISTRY}/${NAMESPACE}/pystrument-frontend:${VERSION}"
CELERY_IMAGE="${REGISTRY}/${NAMESPACE}/pystrument-celery:${VERSION}"

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

# 构建后端镜像
build_backend() {
    print_info "构建后端服务镜像..."
    cd backend
    docker build -t ${BACKEND_IMAGE} .
    cd ..
    print_success "后端镜像构建完成: ${BACKEND_IMAGE}"
}

# 构建前端镜像
build_frontend() {
    print_info "构建前端服务镜像..."
    cd frontend
    docker build -t ${FRONTEND_IMAGE} .
    cd ..
    print_success "前端镜像构建完成: ${FRONTEND_IMAGE}"
}

# 构建Celery镜像
build_celery() {
    print_info "构建Celery服务镜像..."
    cd backend
    docker build -t ${CELERY_IMAGE} .
    cd ..
    print_success "Celery镜像构建完成: ${CELERY_IMAGE}"
}

# 推送镜像
push_images() {
    print_info "开始推送镜像到阿里云仓库..."
    
    print_info "推送后端镜像..."
    docker push ${BACKEND_IMAGE}
    print_success "后端镜像推送完成"
    
    print_info "推送前端镜像..."
    docker push ${FRONTEND_IMAGE}
    print_success "前端镜像推送完成"
    
    print_info "推送Celery镜像..."
    docker push ${CELERY_IMAGE}
    print_success "Celery镜像推送完成"
}

# 验证镜像
verify_images() {
    print_info "验证镜像上传成功..."
    
    docker pull ${BACKEND_IMAGE}
    docker pull ${FRONTEND_IMAGE}
    docker pull ${CELERY_IMAGE}
    
    print_success "所有镜像验证通过"
}

# 显示镜像信息
show_images() {
    print_info "镜像信息汇总:"
    echo "后端镜像: ${BACKEND_IMAGE}"
    echo "前端镜像: ${FRONTEND_IMAGE}"
    echo "Celery镜像: ${CELERY_IMAGE}"
    echo ""
    echo "使用示例:"
    echo "docker pull ${BACKEND_IMAGE}"
    echo "docker pull ${FRONTEND_IMAGE}"
    echo "docker pull ${CELERY_IMAGE}"
}

# 主函数
main() {
    print_info "开始构建并推送V2.0版本镜像到阿里云仓库"
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
    build_backend
    build_frontend
    build_celery
    push_images
    verify_images
    show_images
    
    print_success "所有镜像构建和推送完成！"
}

# 执行主函数
main "$@"