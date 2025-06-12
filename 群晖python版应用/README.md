# 群晖Python版应用

## 📖 项目简介

这是一个专为群晖NAS设计的Python应用程序，具有以下特点：

- 🚀 **单文件脚本**: 所有功能集成在一个Python文件中，便于部署和管理
- ⚙️ **自动配置**: 首次运行自动生成配置文件，无需手动创建
- 📝 **详细注释**: 代码和配置都有非常详细的中文注释，适合Python初学者
- 🔧 **灵活配置**: 支持多种配置选项，可根据需要自定义
- 📊 **日志系统**: 完整的日志记录功能，便于调试和监控
- 🛡️ **错误处理**: 完善的异常处理机制，提高程序稳定性

## 📁 文件结构

```
群晖python版应用/
├── synology_app.py    # 主程序文件
├── README.md          # 说明文档（本文件）
├── config.json        # 配置文件（首次运行自动生成）
└── logs/              # 日志目录（自动创建）
    └── app.log        # 应用日志文件
```

## 🚀 快速开始

### 1. 运行程序

```bash
# 进入应用目录
cd 群晖python版应用

# 运行程序（首次运行会自动生成配置文件）
python3 synology_app.py
```

### 2. 首次运行

首次运行时，程序会：
1. 自动创建 `config.json` 配置文件
2. 创建 `logs` 目录和日志文件
3. 显示配置文件位置和使用说明
4. 开始运行主程序

### 3. 停止程序

按 `Ctrl + C` 可以安全停止程序

## ⚙️ 配置说明

配置文件 `config.json` 包含以下配置节：

### app_info - 应用信息
```json
{
    "name": "群晖Python应用",           // 应用名称
    "version": "1.0.0",               // 版本号
    "description": "应用描述",         // 应用描述
    "author": "OpenHands AI",         // 作者
    "created_time": "2024-01-01..."   // 创建时间
}
```

### app_settings - 应用设置
```json
{
    "debug_mode": false,        // 调试模式（true=开启详细日志）
    "auto_start": true,         // 自动启动
    "check_interval": 60,       // 检查间隔（秒）
    "max_log_size": 10,         // 最大日志文件大小（MB）
    "log_retention_days": 30    // 日志保留天数
}
```

### network - 网络设置
```json
{
    "host": "0.0.0.0",         // 监听地址
    "port": 8080,              // 监听端口
    "timeout": 30,             // 网络超时（秒）
    "max_connections": 100     // 最大连接数
}
```

### database - 数据库设置
```json
{
    "type": "sqlite",          // 数据库类型
    "path": "data/app.db",     // 数据库文件路径
    "backup_enabled": true,    // 启用备份
    "backup_interval": 24      // 备份间隔（小时）
}
```

### security - 安全设置
```json
{
    "enable_auth": false,      // 启用身份验证
    "session_timeout": 3600,   // 会话超时（秒）
    "max_login_attempts": 5,   // 最大登录尝试次数
    "password_min_length": 8   // 密码最小长度
}
```

### notifications - 通知设置
```json
{
    "email_enabled": false,           // 启用邮件通知
    "email_smtp_server": "",          // SMTP服务器
    "email_smtp_port": 587,           // SMTP端口
    "email_username": "",             // 邮箱用户名
    "email_password": "",             // 邮箱密码
    "notification_level": "error"     // 通知级别
}
```

### custom - 自定义设置
```json
{
    "user_name": "admin",             // 用户名
    "language": "zh-CN",              // 界面语言
    "theme": "default",               // 界面主题
    "timezone": "Asia/Shanghai"       // 时区
}
```

## 🔧 自定义开发

### 修改主要业务逻辑

在 `synology_app.py` 文件中找到 `run_main_application` 方法，这里是主要的业务逻辑代码：

```python
def run_main_application(self) -> None:
    """
    运行主应用程序
    
    在这里添加你的主要业务逻辑
    """
    # 你的代码逻辑写在这里
    pass
```

### 添加新的配置项

1. 在 `_create_default_config` 方法中添加新的配置项
2. 使用 `get_config_value` 方法读取配置
3. 使用 `update_config_value` 方法更新配置

### 示例：添加新功能

```python
# 读取配置
my_setting = self.get_config_value('custom', 'my_new_setting', 'default_value')

# 更新配置
self.update_config_value('custom', 'my_new_setting', 'new_value')
```

## 📊 日志系统

### 日志级别
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息

### 使用日志
```python
self.logger.info("这是一条信息日志")
self.logger.warning("这是一条警告日志")
self.logger.error("这是一条错误日志")
```

### 日志文件位置
- 日志文件：`logs/app.log`
- 日志会同时输出到文件和控制台
- 支持中文字符

## 🛠️ 常见问题

### Q: 如何重置配置文件？
A: 删除 `config.json` 文件，重新运行程序即可自动生成新的配置文件。

### Q: 如何修改配置？
A: 直接编辑 `config.json` 文件，保存后重新运行程序即可生效。

### Q: 程序运行出错怎么办？
A: 查看 `logs/app.log` 日志文件，里面有详细的错误信息。

### Q: 如何在群晖上运行？
A: 
1. 将整个文件夹上传到群晖
2. 通过SSH连接到群晖
3. 进入应用目录运行 `python3 synology_app.py`

### Q: 如何设置开机自启动？
A: 可以通过群晖的任务计划功能设置开机自动运行脚本。

## 📝 开发说明

### 代码特点
- **面向对象设计**: 使用类封装功能，便于扩展
- **类型提示**: 使用Python类型提示，提高代码可读性
- **异常处理**: 完善的try-catch机制
- **文档字符串**: 每个函数都有详细的文档说明

### 适合人群
- Python初学者：代码注释详细，便于学习
- 群晖用户：专为群晖NAS环境设计
- 开发者：可以基于此框架快速开发应用

## 📞 技术支持

如果在使用过程中遇到问题，可以：
1. 查看日志文件获取错误信息
2. 检查配置文件格式是否正确
3. 确认Python版本兼容性（建议Python 3.6+）

## 📄 许可证

本项目采用MIT许可证，可以自由使用和修改。

---

**祝你使用愉快！** 🎉