# 🚀 OpenDevinAI520 快速启动指南

## 📋 项目概述

OpenDevinAI520 是一个实用工具开发平台，包含7个核心工具，秉承"人人为我，我为人人"的理念。

## 🛠️ 系统要求

- Python 3.8+
- Git
- 网络连接（用于安装依赖）

## ⚡ 快速启动

### 方法1：一键启动（推荐）

```bash
# 克隆仓库
git clone https://github.com/1525745393/OpenDevinAI520.git
cd OpenDevinAI520

# 一键启动（自动安装依赖）
chmod +x start.sh
./start.sh
```

### 方法2：手动启动

```bash
# 1. 克隆仓库
git clone https://github.com/1525745393/OpenDevinAI520.git
cd OpenDevinAI520

# 2. 安装依赖
pip install -r requirements.txt

# 3. 创建必要目录
mkdir -p logs uploads downloads temp

# 4. 启动主程序
python src/main.py
```

### 方法3：Docker启动

```bash
# 克隆仓库
git clone https://github.com/1525745393/OpenDevinAI520.git
cd OpenDevinAI520

# 使用Docker Compose启动
docker-compose up -d

# 访问Web界面
open http://localhost:5000
```

## 🎯 使用方式

### 1. 命令行模式

```bash
# 查看所有可用工具
python src/main.py --list-tools

# 交互式使用
python src/main.py

# 直接使用特定工具
python -m src.tools.code_formatter format ./my_code.py
python -m src.tools.log_analyzer analyze ./app.log
python -m src.tools.data_converter convert data.json --to csv
```

### 2. Web界面模式

```bash
# 启动Web服务器
python web/app.py

# 访问 http://localhost:5000
```

### 3. 工具模块直接调用

```bash
# 代码格式化
python -m src.tools.code_formatter format ./src --recursive

# 文件批量处理
python -m src.tools.file_processor rename ./photos --pattern "IMG_*.jpg" --format "photo_{counter:03d}.jpg"

# API测试
python -m src.tools.api_tester test https://api.example.com/users

# 数据转换
python -m src.tools.data_converter convert data.json --to yaml --output data.yaml

# 日志分析
python -m src.tools.log_analyzer analyze ./logs/app.log --output report.json

# 媒体文件重命名
python -m src.tools.media_renamer scan ./movies --auto-rename

# 环境配置
python -m src.tools.env_configurator setup python ./my_project
```

## 📊 可用工具

| 工具 | 功能 | 命令示例 |
|------|------|----------|
| 🎨 代码格式化工具 | 格式化Python/JS/TS/JSON/CSS代码 | `python -m src.tools.code_formatter format ./src` |
| 📁 文件批量处理工具 | 批量重命名、复制、移动文件 | `python -m src.tools.file_processor rename ./files` |
| 🌐 API测试工具 | 测试REST API接口 | `python -m src.tools.api_tester test https://api.example.com` |
| 🎬 媒体文件重命名工具 | 智能重命名电影、电视剧文件 | `python -m src.tools.media_renamer scan ./movies` |
| 🔄 数据转换工具 | 转换JSON/CSV/XML/YAML/Excel格式 | `python -m src.tools.data_converter convert data.json --to csv` |
| ⚙️ 环境配置工具 | 配置开发环境 | `python -m src.tools.env_configurator setup python ./project` |
| 📊 日志分析工具 | 分析应用日志文件 | `python -m src.tools.log_analyzer analyze ./app.log` |

## 🔧 配置

### 环境变量配置

创建 `.env` 文件：

```bash
# 日志级别
LOG_LEVEL=INFO

# 工作目录
WORK_DIR=./workspace

# API配置
API_TIMEOUT=30
API_RETRIES=3

# Web服务配置
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_DEBUG=False
```

### 工具配置

编辑 `config/config.yaml`：

```yaml
# 代码格式化配置
code_formatter:
  line_length: 88
  skip_string_normalization: false

# 文件处理配置
file_processor:
  backup_enabled: true
  backup_dir: "./backups"

# API测试配置
api_tester:
  timeout: 30
  retries: 3
  verify_ssl: true
```

## 🐛 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

2. **权限错误**
   ```bash
   # Linux/Mac
   chmod +x start.sh
   
   # Windows
   # 以管理员身份运行命令提示符
   ```

3. **端口占用**
   ```bash
   # 查看端口占用
   netstat -tulpn | grep :5000
   
   # 修改端口
   export WEB_PORT=8080
   python web/app.py
   ```

4. **Python版本问题**
   ```bash
   # 检查Python版本
   python --version
   
   # 使用Python 3.8+
   python3.8 src/main.py
   ```

## 📚 更多资源

- 📖 [完整文档](./docs/)
- 🔧 [API参考](./docs/api-reference.md)
- 🤝 [贡献指南](./CONTRIBUTING.md)
- 💬 [社区讨论](https://github.com/1525745393/OpenDevinAI520/issues/1)
- 🐛 [问题报告](https://github.com/1525745393/OpenDevinAI520/issues)

## 🎉 开始使用

现在您可以开始使用 OpenDevinAI520 了！

```bash
# 快速体验
python src/main.py --list-tools
python src/main.py
```

---

**"人人为我，我为人人"** - 欢迎加入我们的开源社区！🚀