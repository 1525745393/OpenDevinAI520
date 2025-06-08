# OpenDevinAI520 Docker镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV OPENDEVINAI520_ENV=production

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装Node.js (用于前端工具)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# 复制依赖文件
COPY requirements.txt package.json ./

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 安装Node.js依赖
RUN npm install

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p logs uploads downloads temp

# 设置权限
RUN chmod +x deploy.sh

# 暴露端口
EXPOSE 12000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:12000/api/tools || exit 1

# 启动命令
CMD ["python", "web/app.py"]