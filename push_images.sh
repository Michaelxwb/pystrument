#!/bin/bash

# 阿里云镜像仓库推送脚本
REGISTRY="crpi-x3k4zm1fio56r4y0.cn-shenzhen.personal.cr.aliyuncs.com"
NAMESPACE="xwbclound_hub"
VERSION="v2.0"

echo "=== 阿里云镜像仓库推送脚本 ==="
echo "镜像仓库: ${REGISTRY}/${NAMESPACE}"
echo "版本: ${VERSION}"
echo ""

# 显示当前镜像
echo "当前镜像列表:"
docker images | grep ${NAMESPACE} | grep ${VERSION}

echo ""
echo "请手动执行以下命令登录阿里云镜像仓库:"
echo "docker login ${REGISTRY}"
echo ""

echo "登录后，执行以下命令推送镜像:"
echo ""
echo "# 推送后端镜像"
echo "docker push ${REGISTRY}/${NAMESPACE}/pystrument-backend:${VERSION}"
echo ""
echo "# 推送前端镜像"
echo "docker push ${REGISTRY}/${NAMESPACE}/pystrument-frontend:${VERSION}"
echo ""
echo "# 推送Celery镜像"
echo "docker push ${REGISTRY}/${NAMESPACE}/pystrument-celery:${VERSION}"
echo ""

echo "=== 镜像信息汇总 ==="
echo "后端镜像: ${REGISTRY}/${NAMESPACE}/pystrument-backend:${VERSION}"
echo "前端镜像: ${REGISTRY}/${NAMESPACE}/pystrument-frontend:${VERSION}"
echo "Celery镜像: ${REGISTRY}/${NAMESPACE}/pystrument-celery:${VERSION}"