# 快速开始

本指南将帮助您快速上手 OpenDevinAI520 实用工具平台。

## 📋 系统要求

- Python 3.8 或更高版本
- 操作系统：Windows、macOS、Linux

## 🔧 安装

### 1. 克隆项目
```bash
git clone https://github.com/1525745393/OpenDevinAI520.git
cd OpenDevinAI520
```

### 2. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 3. 安装可选依赖

#### 代码格式化工具
```bash
# Python代码格式化
pip install black autopep8

# JavaScript/TypeScript格式化
npm install -g prettier
```

#### Node.js依赖（可选）
```bash
npm install
```

## 🚀 运行程序

### 命令行模式
```bash
python src/main.py
```

### 直接执行工具
```bash
# 查看所有可用工具
python -c "from src.tools import ToolManager; tm = ToolManager({}); print(tm.list_tools())"
```

## 🎯 第一次使用

### 1. 启动程序
```bash
python src/main.py
```

您将看到欢迎界面：
```
╔══════════════════════════════════════════════════════════════╗
║                    OpenDevinAI520                            ║
║                  实用工具开发平台                              ║
║                                                              ║
║              人人为我，我为人人                                ║
║          让我们一起构建更好的开发工具生态！                      ║
╚══════════════════════════════════════════════════════════════╝
```

### 2. 查看帮助
```
🛠️  OpenDevinAI520> help
```

### 3. 列出可用工具
```
🛠️  OpenDevinAI520> list
```

## 📖 基本命令

### 通用命令
- `help` - 显示帮助信息
- `list` - 列出所有可用工具
- `exit` - 退出程序

### 工具命令格式
```
<工具名> <操作> [参数...]
```

## 🛠️ 工具使用示例

### 代码格式化
```bash
# 格式化单个文件
code_formatter format example.py

# 格式化整个目录
code_formatter format src/

# 查看工具帮助
code_formatter help
```

### 文件批量处理
```bash
# 批量重命名
file_processor batch_rename "*.txt" "backup_*.txt"

# 查找重复文件
file_processor find_duplicates ./downloads/

# 组织文件
file_processor organize ./messy_folder/
```

### 影视文件重命名
```bash
# 自动识别并重命名
media_renamer auto_rename ./downloads/

# 分析文件信息
media_renamer analyze ./movies/

# 组织到不同目录
media_renamer organize ./downloads/ ./organized/
```

### API测试
```bash
# 测试单个API
api_tester test https://api.example.com/users

# 批量测试
api_tester batch_test tests.json

# 负载测试
api_tester load_test https://api.example.com 10 60
```

### 数据转换
```bash
# JSON转CSV
data_converter json_to_csv data.json data.csv

# 格式化JSON
data_converter format_json messy.json clean.json

# YAML转JSON
data_converter yaml_to_json config.yaml config.json
```

## ⚙️ 配置

### 默认配置文件
程序首次运行时会自动创建 `config.yaml` 配置文件：

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

### 环境变量
您可以使用环境变量覆盖配置：

```bash
export OPENDEVINAI520_DEBUG=true
export OPENDEVINAI520_LOG_LEVEL=DEBUG
```

## 🔍 故障排除

### 常见问题

#### 1. 导入错误
```
ModuleNotFoundError: No module named 'xxx'
```
**解决方案：** 确保已安装所有依赖
```bash
pip install -r requirements.txt
```

#### 2. 权限错误
```
PermissionError: [Errno 13] Permission denied
```
**解决方案：** 检查文件权限或使用管理员权限运行

#### 3. 编码错误
```
UnicodeDecodeError: 'utf-8' codec can't decode
```
**解决方案：** 确保文件使用UTF-8编码

### 获取帮助

1. **查看工具帮助**
   ```
   <工具名> help
   ```

2. **查看日志**
   ```bash
   tail -f logs/opendevinai520_*.log
   ```

3. **提交问题**
   - GitHub Issues: https://github.com/1525745393/OpenDevinAI520/issues

## 🎉 下一步

- 阅读 [工具指南](tools-guide.md) 了解各工具的详细用法
- 查看 [API文档](api-reference.md) 了解编程接口
- 参考 [配置说明](configuration.md) 自定义配置
- 阅读 [开发指南](development.md) 参与项目开发

---

**恭喜！您已经成功开始使用 OpenDevinAI520！** 🎊