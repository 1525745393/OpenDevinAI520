# 贡献指南

欢迎来到 OpenDevinAI520 社区！我们非常感谢您对项目的关注和贡献意愿。

## 🤝 贡献方式

### 1. 报告问题 🐛

发现了bug或有改进建议？请通过以下方式报告：

1. 在 [GitHub Issues](https://github.com/1525745393/OpenDevinAI520/issues) 创建新issue
2. 使用合适的issue模板
3. 提供详细的问题描述和复现步骤

#### Bug报告模板

```markdown
**问题描述**
简要描述遇到的问题

**复现步骤**
1. 执行命令 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

**期望行为**
描述您期望发生的情况

**实际行为**
描述实际发生的情况

**环境信息**
- OS: [e.g. Ubuntu 20.04]
- Python版本: [e.g. 3.9.0]
- 项目版本: [e.g. 1.0.0]

**附加信息**
添加任何其他相关信息、截图等
```

### 2. 功能建议 💡

有新功能想法？我们很乐意听到！

1. 在 [GitHub Discussions](https://github.com/1525745393/OpenDevinAI520/discussions) 发起讨论
2. 详细描述功能需求和使用场景
3. 与社区成员讨论可行性

### 3. 代码贡献 🔧

#### 开发环境设置

```bash
# 1. Fork 仓库并克隆
git clone https://github.com/YOUR_USERNAME/OpenDevinAI520.git
cd OpenDevinAI520

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 安装pre-commit钩子
pre-commit install

# 5. 运行测试确保环境正常
python -m pytest tests/
```

#### 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **编写代码**
   - 遵循项目的代码规范
   - 添加必要的测试
   - 更新相关文档

3. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **推送并创建PR**
   ```bash
   git push origin feature/your-feature-name
   ```

#### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型说明：**
- `feat`: 新功能
- `fix`: bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(api-tester): add support for GraphQL queries

Add GraphQL query support to the API testing tool.
This includes query validation and response parsing.

Closes #123
```

### 4. 文档贡献 📝

文档同样重要！您可以：

- 修复文档中的错误
- 添加使用示例
- 翻译文档到其他语言
- 改进文档结构

## 📋 代码规范

### Python代码规范

我们遵循 [PEP 8](https://pep8.org/) 和以下额外规范：

1. **代码格式化**
   ```bash
   # 使用 black 格式化代码
   black src/
   
   # 使用 isort 排序导入
   isort src/
   ```

2. **代码检查**
   ```bash
   # 使用 flake8 检查代码质量
   flake8 src/
   
   # 使用 mypy 进行类型检查
   mypy src/
   ```

3. **命名规范**
   - 类名：`PascalCase`
   - 函数和变量：`snake_case`
   - 常量：`UPPER_SNAKE_CASE`
   - 私有成员：`_leading_underscore`

4. **文档字符串**
   ```python
   def example_function(param1: str, param2: int) -> bool:
       """
       函数的简要描述
       
       Args:
           param1: 参数1的描述
           param2: 参数2的描述
       
       Returns:
           返回值的描述
       
       Raises:
           ValueError: 当参数无效时抛出
       """
       pass
   ```

### JavaScript/TypeScript代码规范

1. **使用 Prettier 格式化**
   ```bash
   npx prettier --write src/
   ```

2. **使用 ESLint 检查**
   ```bash
   npx eslint src/
   ```

## 🧪 测试指南

### 编写测试

1. **单元测试**
   ```python
   import unittest
   from tools.code_formatter import CodeFormatter
   
   class TestCodeFormatter(unittest.TestCase):
       def setUp(self):
           self.formatter = CodeFormatter()
       
       def test_detect_language(self):
           self.assertEqual(
               self.formatter.detect_language('test.py'), 
               'python'
           )
   ```

2. **集成测试**
   ```python
   def test_format_directory_integration():
       # 创建测试目录和文件
       # 执行格式化
       # 验证结果
       pass
   ```

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_code_formatter.py

# 运行测试并生成覆盖率报告
python -m pytest --cov=src --cov-report=html

# 运行性能测试
python -m pytest --benchmark-only
```

## 🔍 代码审查

### Pull Request 检查清单

在提交PR之前，请确保：

- [ ] 代码通过所有测试
- [ ] 代码符合项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 提交信息符合规范
- [ ] 没有引入新的依赖（如有，请说明原因）

### 审查标准

我们的代码审查关注：

1. **功能正确性** - 代码是否按预期工作
2. **代码质量** - 是否遵循最佳实践
3. **性能** - 是否有性能问题
4. **安全性** - 是否存在安全隐患
5. **可维护性** - 代码是否易于理解和维护

## 🏷️ 发布流程

### 版本号规范

我们使用 [语义化版本](https://semver.org/)：

- `MAJOR.MINOR.PATCH`
- `1.0.0` → `1.0.1` (补丁版本)
- `1.0.0` → `1.1.0` (次要版本)
- `1.0.0` → `2.0.0` (主要版本)

### 发布步骤

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 触发自动发布流程

## 🎯 贡献者权益

### 认可方式

- 在 README 中列出贡献者
- 在发布说明中感谢贡献者
- 为活跃贡献者提供项目权限

### 贡献者等级

1. **贡献者** - 提交过代码或文档
2. **协作者** - 定期贡献，有项目写权限
3. **维护者** - 负责项目方向和重大决策

## 📞 获取帮助

遇到问题？可以通过以下方式获取帮助：

- 💬 [GitHub Discussions](https://github.com/1525745393/OpenDevinAI520/discussions) - 一般讨论和问题
- 🐛 [GitHub Issues](https://github.com/1525745393/OpenDevinAI520/issues) - Bug报告和功能请求
- 📧 Email: [项目邮箱] - 私人或敏感问题

## 🌟 特别感谢

感谢所有为项目做出贡献的开发者！

### 核心贡献者

- [@1525745393](https://github.com/1525745393) - 项目创始人

### 贡献者列表

<a href="https://github.com/1525745393/OpenDevinAI520/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=1525745393/OpenDevinAI520" />
</a>

---

**人人为我，我为人人 - 让我们一起构建更好的开发工具生态！** 🚀

> 记住：每一个贡献，无论大小，都是宝贵的。感谢您成为 OpenDevinAI520 社区的一员！