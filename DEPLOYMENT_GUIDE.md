# OpenDevinAI520 部署指南

## 🚀 GitHub仓库创建和上传

由于当前环境的GitHub token权限限制，需要手动创建仓库。以下是完整的步骤：

### 1. 创建GitHub仓库

1. **访问GitHub**: 打开 [https://github.com/new](https://github.com/new)

2. **填写仓库信息**:
   - **Repository name**: `OpenDevinAI520`
   - **Description**: `实用工具开发平台 - 自用人人为我我为人人，致力于创建高效便民的开发工具集`
   - **Visibility**: Public (公开)
   - **Initialize repository**: 
     - ❌ 不要勾选 "Add a README file"
     - ❌ 不要选择 .gitignore
     - ❌ 不要选择 License (我们已经有了)

3. **点击 "Create repository"**

### 2. 上传本地代码

在您的本地终端中执行以下命令：

```bash
# 进入项目目录
cd /workspace/OpenDevinAI520

# 添加远程仓库 (替换为您的GitHub用户名)
git remote add origin https://github.com/1525745393/OpenDevinAI520.git

# 推送代码到GitHub
git push -u origin main
```

### 3. 验证上传

访问 `https://github.com/1525745393/OpenDevinAI520` 确认代码已成功上传。

## 🌐 启用GitHub Pages

### 自动启用 (推荐)

代码上传后，GitHub Actions会自动构建和部署文档到GitHub Pages：

1. 访问仓库的 **Actions** 标签页
2. 等待CI/CD流程完成
3. 访问 `https://1525745393.github.io/OpenDevinAI520/` 查看文档

### 手动启用

如果自动部署失败，可以手动启用：

1. 进入仓库 **Settings** → **Pages**
2. **Source**: 选择 "Deploy from a branch"
3. **Branch**: 选择 "gh-pages" 分支
4. **Folder**: 选择 "/ (root)"
5. 点击 **Save**

## 🛠️ 本地开发环境搭建

### 方式一：使用部署脚本 (推荐)

```bash
# 克隆仓库
git clone https://github.com/1525745393/OpenDevinAI520.git
cd OpenDevinAI520

# 运行部署脚本
./deploy.sh

# 或指定模式
./deploy.sh web          # Web模式
./deploy.sh --dev cli    # 开发模式
```

### 方式二：手动安装

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 创建必要目录
mkdir -p logs uploads downloads temp

# 4. 运行程序
python src/main.py        # 命令行模式
python web/app.py         # Web模式
```

### 方式三：Docker部署

```bash
# 克隆仓库
git clone https://github.com/1525745393/OpenDevinAI520.git
cd OpenDevinAI520

# 使用Docker Compose启动
docker-compose up -d

# 访问应用
# Web界面: http://localhost:12000
# API文档: http://localhost:12000/docs
```

## 📊 功能验证

### 1. 命令行模式测试

```bash
# 启动程序
python src/main.py

# 在交互界面中测试
🛠️  OpenDevinAI520> help
🛠️  OpenDevinAI520> list
🛠️  OpenDevinAI520> code_formatter help
🛠️  OpenDevinAI520> exit
```

### 2. Web模式测试

```bash
# 启动Web服务器
python web/app.py

# 访问以下URL测试
# http://localhost:12000/          # 主页
# http://localhost:12000/api/tools # API接口
```

### 3. 工具功能测试

```bash
# 代码格式化测试
echo 'def hello( ):print("hello")' > test.py
python src/main.py
🛠️  OpenDevinAI520> code_formatter format test.py

# API测试
🛠️  OpenDevinAI520> api_tester test https://httpbin.org/get

# 数据转换测试
🛠️  OpenDevinAI520> data_converter json_to_csv examples/sample_data.json output.csv
```

## 🔧 配置说明

### 环境变量

```bash
# 调试模式
export OPENDEVINAI520_DEBUG=true

# 日志级别
export OPENDEVINAI520_LOG_LEVEL=DEBUG

# Web端口
export OPENDEVINAI520_WEB_PORT=12000
```

### 配置文件

编辑 `config.yaml` 文件：

```yaml
app:
  name: OpenDevinAI520
  version: 1.0.0
  debug: false

tools:
  enabled:
    - code_formatter
    - file_processor
    - api_tester
    - data_converter
    - media_renamer

logging:
  level: INFO
  file_enabled: true
```

## 🚨 故障排除

### 常见问题

1. **导入错误**
   ```bash
   # 确保在项目根目录
   export PYTHONPATH=/path/to/OpenDevinAI520
   ```

2. **权限错误**
   ```bash
   # 给脚本执行权限
   chmod +x deploy.sh
   ```

3. **端口占用**
   ```bash
   # 检查端口占用
   lsof -i :12000
   
   # 修改端口
   export OPENDEVINAI520_WEB_PORT=12001
   ```

4. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 清理缓存
   pip cache purge
   ```

### 日志查看

```bash
# 查看应用日志
tail -f logs/opendevinai520_*.log

# 查看Web服务器日志
tail -f logs/web_*.log
```

## 📈 性能优化

### 生产环境建议

1. **使用Gunicorn运行Web应用**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:12000 web.app:app
   ```

2. **配置Nginx反向代理**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:12000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **启用Redis缓存**
   ```bash
   # 启动Redis
   docker run -d -p 6379:6379 redis:alpine
   
   # 在配置中启用缓存
   export OPENDEVINAI520_REDIS_URL=redis://localhost:6379
   ```

## 🤝 贡献指南

### 开发流程

1. **Fork仓库**
2. **创建功能分支**
   ```bash
   git checkout -b feature/new-tool
   ```
3. **开发和测试**
   ```bash
   # 运行测试
   pytest tests/
   
   # 代码检查
   flake8 src/
   black src/
   ```
4. **提交更改**
   ```bash
   git commit -m "feat: 添加新工具"
   ```
5. **创建Pull Request**

### 代码规范

- 遵循PEP 8
- 使用Black格式化代码
- 编写单元测试
- 更新文档

## 📞 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/1525745393/OpenDevinAI520/issues)
- **GitHub Discussions**: [参与讨论](https://github.com/1525745393/OpenDevinAI520/discussions)
- **文档**: [在线文档](https://1525745393.github.io/OpenDevinAI520/)

---

**🎉 恭喜！您已经成功部署了OpenDevinAI520！**

**人人为我，我为人人 - 让我们一起构建更好的开发工具生态！**