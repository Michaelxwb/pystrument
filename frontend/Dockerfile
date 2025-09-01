# 多阶段构建
ARG NODE_VERSION=18

# 构建阶段
FROM node:${NODE_VERSION}-alpine as builder

# 更换为清华大学镜像源以提高下载速度
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories && \
    apk add --no-cache python3 make g++ git

# 设置工作目录
WORKDIR /app

# 设置npm镜像源（加速构建）
RUN npm config set registry https://registry.npmmirror.com/

# 复制package文件
COPY package*.json ./

# 安装依赖 - 解决Rollup可选依赖问题
RUN echo "Installing dependencies..." && \
    npm ci --only=production --prefer-offline --no-audit --no-progress --include=optional || \
    (echo "Retrying dependency installation..." && \
     npm install --prefer-offline --no-audit --no-progress --include=optional)

# 复制源码
COPY . .

# 构建应用 - 添加错误处理和Rollup问题解决
RUN echo "Building application..." && \
    npm run build || \
    (echo "Build failed, installing platform-specific Rollup dependencies..." && \
     npm install @rollup/rollup-linux-arm64-musl --prefer-offline --no-audit --no-progress || \
     npm install @rollup/rollup-linux-x64-musl --prefer-offline --no-audit --no-progress || \
     echo "Continuing with build..." && \
     npm run build)

# 开发阶段
FROM node:${NODE_VERSION}-alpine as development

# 更换为清华大学镜像源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories && \
    apk add --no-cache python3 make g++ git

# 设置工作目录
WORKDIR /app

# 设置npm镜像源
RUN npm config set registry https://registry.npmmirror.com/

# 复制package文件
COPY package*.json ./

# 安装所有依赖（包括开发依赖）
RUN npm install --prefer-offline --no-audit --no-progress --include=optional

# 复制源码
COPY . .

# 暴露端口
EXPOSE 3000

# 开发环境启动命令
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# 生产阶段
FROM nginx:alpine as production

# 更换为清华大学镜像源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories && \
    apk add --no-cache curl

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]

# 默认使用生产阶段
FROM production