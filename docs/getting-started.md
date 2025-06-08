# 快速开始指南

欢迎使用 OpenDevinAI520！本指南将帮助您快速上手使用我们的实用工具集。

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/1525745393/OpenDevinAI520.git
cd OpenDevinAI520
```

### 2. 安装Python依赖

```bash
# 使用pip安装
pip install -r requirements.txt

# 或使用虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 安装Node.js依赖（可选）

如果您需要使用Node.js相关功能：

```bash
npm install
```

### 4. 验证安装

```bash
python src/main.py --version
python src/main.py --list-tools
```

## 第一个示例

让我们从一个简单的例子开始：

### 运行Hello World示例

```bash
python examples/hello_world.py
```

您应该看到一个漂亮的欢迎界面，这表明安装成功！

## 核心工具使用

### 1. 代码格式化工具

#### 格式化Python文件

```bash
# 创建一个测试文件
echo "def hello():print('Hello World')" > test.py

# 格式化文件
python -m src.tools.code_formatter test.py

# 查看结果
cat test.py
```

#### 格式化整个项目

```bash
# 格式化src目录下的所有Python文件
python -m src.tools.code_formatter src/ --recursive --report
```

### 2. 文件批量处理工具

#### 批量重命名文件

```bash
# 创建测试文件
mkdir test_files
touch test_files/old_file1.txt test_files/old_file2.txt test_files/old_file3.txt

# 预览重命名效果
python -m src.tools.file_processor rename test_files "old_" "new_" --preview

# 执行重命名
python -m src.tools.file_processor rename test_files "old_" "new_"

# 查看结果
ls test_files/
```

#### 组织文件

```bash
# 创建不同类型的文件
touch test_files/document.pdf test_files/image.jpg test_files/script.py

# 按扩展名组织文件
python -m src.tools.file_processor organize test_files

# 查看结果
tree test_files/  # 或 ls -la test_files/
```

### 3. API测试工具

#### 测试公开API

```bash
# 测试一个公开的API
python -m src.tools.api_tester test GET "https://jsonplaceholder.typicode.com/users/1"

# 测试POST请求
python -m src.tools.api_tester test POST "https://jsonplaceholder.typicode.com/posts" \
  --data '{"title": "Test", "body": "Test content", "userId": 1}'
```

#### 创建测试套件

创建一个测试文件 `api_tests.json`：

```json
[
  {
    "name": "获取用户信息",
    "method": "GET",
    "endpoint": "https://jsonplaceholder.typicode.com/users/1",
    "expected_status": 200
  },
  {
    "name": "获取所有帖子",
    "method": "GET", 
    "endpoint": "https://jsonplaceholder.typicode.com/posts",
    "expected_status": 200
  }
]
```

运行批量测试：

```bash
python -m src.tools.api_tester batch api_tests.json --report test_report.html
```

## 配置和自定义

### 环境变量

您可以通过环境变量配置一些默认行为：

```bash
# 设置默认API基础URL
export OPENDEVIN_API_BASE_URL="https://api.example.com"

# 设置默认超时时间
export OPENDEVIN_TIMEOUT=60

# 设置默认输出格式
export OPENDEVIN_OUTPUT_FORMAT="json"
```

### 配置文件

创建 `.opendevin.json` 配置文件：

```json
{
  "api": {
    "base_url": "https://api.example.com",
    "timeout": 30,
    "default_headers": {
      "User-Agent": "OpenDevinAI520/1.0"
    }
  },
  "formatter": {
    "python": {
      "line_length": 88,
      "skip_string_normalization": true
    }
  },
  "file_processor": {
    "backup_before_rename": true,
    "confirm_destructive_operations": true
  }
}
```

## 常见使用场景

### 场景1：项目代码整理

```bash
# 1. 格式化所有代码文件
python -m src.tools.code_formatter ./my_project --recursive

# 2. 组织项目文件
python -m src.tools.file_processor organize ./my_project/downloads

# 3. 清理空目录
python -m src.tools.file_processor clean ./my_project
```

### 场景2：API开发测试

```bash
# 1. 创建API测试套件
cat > my_api_tests.json << EOF
[
  {
    "name": "健康检查",
    "method": "GET",
    "endpoint": "/health",
    "expected_status": 200
  },
  {
    "name": "用户认证",
    "method": "POST",
    "endpoint": "/auth/login",
    "data": {"username": "test", "password": "test123"},
    "expected_status": 200
  }
]
EOF

# 2. 运行测试
python -m src.tools.api_tester batch my_api_tests.json \
  --base-url "http://localhost:3000" \
  --report api_report.html

# 3. 查看报告
open api_report.html  # macOS
# 或 start api_report.html  # Windows
# 或 xdg-open api_report.html  # Linux
```

### 场景3：文件批量处理

```bash
# 1. 批量重命名照片文件
python -m src.tools.file_processor rename ./photos \
  "IMG_(\d{8})_(\d{6})" "photo_\1_\2" --preview

# 2. 确认无误后执行
python -m src.tools.file_processor rename ./photos \
  "IMG_(\d{8})_(\d{6})" "photo_\1_\2"

# 3. 按日期组织照片
python -m src.tools.file_processor organize ./photos
```

## 故障排除

### 常见问题

#### 1. 导入错误

```
ModuleNotFoundError: No module named 'rich'
```

**解决方案：**
```bash
pip install -r requirements.txt
```

#### 2. 权限错误

```
PermissionError: [Errno 13] Permission denied
```

**解决方案：**
```bash
# 检查文件权限
ls -la filename

# 修改权限
chmod 644 filename
```

#### 3. 格式化工具未找到

```
格式化工具 black 不可用，请先安装: pip install black
```

**解决方案：**
```bash
pip install black
# 或
npm install -g prettier
```

### 调试技巧

1. **使用详细模式：**
   ```bash
   python -m src.tools.code_formatter ./src --verbose
   ```

2. **检查工具状态：**
   ```bash
   python src/main.py --list-tools
   ```

3. **预览操作：**
   ```bash
   python -m src.tools.file_processor rename ./files "old" "new" --preview
   ```

## 下一步

现在您已经掌握了基本用法，可以：

1. 查看 [API参考文档](api-reference.md) 了解详细的API
2. 阅读 [工具使用指南](tools-guide.md) 学习高级用法
3. 参考 [贡献指南](contributing.md) 参与项目开发

## 获取帮助

- 📖 查看文档：[docs/](.)
- 🐛 报告问题：[GitHub Issues](https://github.com/1525745393/OpenDevinAI520/issues)
- 💬 讨论交流：[GitHub Discussions](https://github.com/1525745393/OpenDevinAI520/discussions)

---

**人人为我，我为人人 - 让我们一起构建更好的开发工具生态！** 🚀