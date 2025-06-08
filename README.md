# OpenDevinAI520

## 项目简介

OpenDevinAI520 是一个实用工具开发平台，秉承"自用人人为我我为人人"的理念，致力于创建高效便民的开发工具集。本项目旨在为开发者提供一系列实用的工具和解决方案，提高开发效率，简化日常工作流程。

## 项目特色

- 🚀 **高效实用** - 专注于解决实际开发中的痛点问题
- 🤝 **开源共享** - 人人为我，我为人人的开源精神
- 🛠️ **工具集合** - 涵盖多种开发场景的实用工具
- 📚 **易于使用** - 简洁明了的API设计和详细的文档

## 功能模块

### 已实现的工具

- [x] **代码格式化工具** - 支持Python, JavaScript, TypeScript, JSON, CSS
- [x] **文件批量处理工具** - 批量重命名、复制、移动、组织文件
- [x] **API测试工具** - REST API测试、批量测试、报告生成

### 计划中的工具

- [ ] 数据转换工具
- [ ] 开发环境配置工具
- [ ] 日志分析工具

## 快速开始

```bash
# 克隆项目
git clone https://github.com/1525745393/OpenDevinAI520.git

# 进入项目目录
cd OpenDevinAI520

# 安装依赖
npm install
# 或者
pip install -r requirements.txt

# 查看可用工具
python src/main.py --list-tools

# 使用示例
# 1. 格式化代码
python -m src.tools.code_formatter ./src

# 2. 批量重命名文件（预览模式）
python -m src.tools.file_processor rename ./files "old_" "new_" --preview

# 3. 测试API
python -m src.tools.api_tester test GET "https://httpbin.org/get"

# 4. 批量API测试
python -m src.tools.api_tester batch examples/api_test_suite.json
```

## 项目结构

```
OpenDevinAI520/
├── README.md           # 项目说明文档
├── LICENSE            # MIT许可证
├── .gitignore         # Git忽略文件
├── package.json       # Node.js依赖配置
├── requirements.txt   # Python依赖配置
├── src/              # 源代码目录
│   ├── tools/        # 工具模块
│   ├── utils/        # 工具函数
│   └── main.py       # 主程序入口
├── docs/             # 文档目录
├── tests/            # 测试目录
└── examples/         # 示例代码
```

## 贡献指南

我们欢迎所有形式的贡献！无论是：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码

### 贡献步骤

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 开发规范

- 代码风格：遵循项目现有的代码风格
- 提交信息：使用清晰、描述性的提交信息
- 测试：为新功能添加相应的测试
- 文档：更新相关文档

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页：[https://github.com/1525745393/OpenDevinAI520](https://github.com/1525745393/OpenDevinAI520)
- 问题反馈：[Issues](https://github.com/1525745393/OpenDevinAI520/issues)

## 致谢

感谢所有为这个项目做出贡献的开发者们！

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

**人人为我，我为人人 - 让我们一起构建更好的开发工具生态！**
