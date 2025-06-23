# 群晖Python应用 - 安装部署指南

## 📋 系统要求

### 群晖NAS要求
- 群晖DSM 6.0 或更高版本
- 已安装Python 3.6 或更高版本
- 至少 100MB 可用存储空间

### Python环境
- Python 3.6+
- 标准库（无需额外安装包）

## 🚀 安装步骤

### 方法一：通过SSH安装（推荐）

#### 1. 启用SSH服务
1. 登录群晖DSM管理界面
2. 进入 `控制面板` → `终端机和SNMP`
3. 勾选 `启动SSH功能`
4. 设置端口（默认22）
5. 点击 `应用`

#### 2. 连接SSH
```bash
# 使用SSH客户端连接群晖
ssh admin@你的群晖IP地址

# 例如：
ssh admin@192.168.1.100
```

#### 3. 上传应用文件
```bash
# 创建应用目录
mkdir -p /volume1/python_apps/synology_app

# 进入目录
cd /volume1/python_apps/synology_app

# 方法A：使用wget下载（如果有网络）
# wget https://your-server.com/synology_app.py

# 方法B：使用scp上传文件
# 在本地电脑执行：
# scp synology_app.py admin@192.168.1.100:/volume1/python_apps/synology_app/
```

#### 4. 设置权限
```bash
# 设置执行权限
chmod +x synology_app.py

# 设置目录权限
chmod 755 /volume1/python_apps/synology_app
```

#### 5. 首次运行
```bash
# 运行应用
python3 synology_app.py
```

### 方法二：通过File Station安装

#### 1. 创建目录
1. 打开 `File Station`
2. 在共享文件夹中创建目录：`python_apps/synology_app`

#### 2. 上传文件
1. 将 `synology_app.py` 和 `README.md` 上传到创建的目录
2. 确保文件上传完整

#### 3. 通过SSH运行
1. 按照方法一的步骤2连接SSH
2. 进入应用目录：
   ```bash
   cd /volume1/python_apps/synology_app
   python3 synology_app.py
   ```

## ⚙️ 配置开机自启动

### 使用任务计划

#### 1. 创建启动脚本
```bash
# 创建启动脚本
cat > /volume1/python_apps/synology_app/start_app.sh << 'EOF'
#!/bin/bash

# 群晖Python应用启动脚本
APP_DIR="/volume1/python_apps/synology_app"
APP_SCRIPT="synology_app.py"
LOG_FILE="$APP_DIR/logs/startup.log"

# 创建日志目录
mkdir -p "$APP_DIR/logs"

# 记录启动时间
echo "$(date): 开始启动群晖Python应用" >> "$LOG_FILE"

# 进入应用目录
cd "$APP_DIR"

# 启动应用（后台运行）
nohup python3 "$APP_SCRIPT" >> "$LOG_FILE" 2>&1 &

# 记录进程ID
echo $! > "$APP_DIR/app.pid"

echo "$(date): 应用启动完成，PID: $!" >> "$LOG_FILE"
EOF

# 设置执行权限
chmod +x /volume1/python_apps/synology_app/start_app.sh
```

#### 2. 创建停止脚本
```bash
# 创建停止脚本
cat > /volume1/python_apps/synology_app/stop_app.sh << 'EOF'
#!/bin/bash

# 群晖Python应用停止脚本
APP_DIR="/volume1/python_apps/synology_app"
PID_FILE="$APP_DIR/app.pid"
LOG_FILE="$APP_DIR/logs/startup.log"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "$(date): 正在停止应用，PID: $PID" >> "$LOG_FILE"
    
    # 尝试优雅停止
    kill -TERM "$PID" 2>/dev/null
    
    # 等待5秒
    sleep 5
    
    # 检查进程是否还在运行
    if kill -0 "$PID" 2>/dev/null; then
        echo "$(date): 强制停止应用" >> "$LOG_FILE"
        kill -KILL "$PID" 2>/dev/null
    fi
    
    # 删除PID文件
    rm -f "$PID_FILE"
    
    echo "$(date): 应用已停止" >> "$LOG_FILE"
else
    echo "$(date): 未找到PID文件，应用可能未运行" >> "$LOG_FILE"
fi
EOF

# 设置执行权限
chmod +x /volume1/python_apps/synology_app/stop_app.sh
```

#### 3. 在DSM中设置任务计划
1. 登录DSM管理界面
2. 进入 `控制面板` → `任务计划`
3. 点击 `新增` → `触发的任务` → `用户定义的脚本`
4. 设置任务名称：`启动群晖Python应用`
5. 用户账号：选择 `root`
6. 事件：选择 `开机`
7. 在 `任务设置` 中输入：
   ```bash
   /volume1/python_apps/synology_app/start_app.sh
   ```
8. 点击 `确定` 保存

## 🔧 高级配置

### 设置环境变量
```bash
# 编辑环境变量文件
cat > /volume1/python_apps/synology_app/.env << 'EOF'
# 应用环境变量
PYTHONPATH=/volume1/python_apps/synology_app
APP_ENV=production
LOG_LEVEL=INFO
EOF
```

### 配置日志轮转
```bash
# 创建日志轮转配置
cat > /volume1/python_apps/synology_app/logrotate.conf << 'EOF'
/volume1/python_apps/synology_app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
```

### 设置防火墙规则
如果应用需要网络访问：
1. 进入 `控制面板` → `安全性` → `防火墙`
2. 编辑规则，添加端口（默认8080）
3. 设置来源IP范围

## 🛠️ 故障排除

### 常见问题

#### 1. Python命令不存在
```bash
# 检查Python安装
which python3
python3 --version

# 如果没有安装，通过套件中心安装Python3
```

#### 2. 权限不足
```bash
# 检查文件权限
ls -la /volume1/python_apps/synology_app/

# 修复权限
chmod 755 /volume1/python_apps/synology_app/
chmod +x /volume1/python_apps/synology_app/synology_app.py
```

#### 3. 端口被占用
```bash
# 检查端口占用
netstat -tulpn | grep 8080

# 修改配置文件中的端口号
```

#### 4. 应用无法启动
```bash
# 查看日志
tail -f /volume1/python_apps/synology_app/logs/app.log

# 手动运行检查错误
cd /volume1/python_apps/synology_app
python3 synology_app.py
```

### 日志文件位置
- 应用日志：`/volume1/python_apps/synology_app/logs/app.log`
- 启动日志：`/volume1/python_apps/synology_app/logs/startup.log`
- 系统日志：`/var/log/messages`

### 性能监控
```bash
# 查看应用进程
ps aux | grep synology_app

# 查看资源使用
top -p $(cat /volume1/python_apps/synology_app/app.pid)

# 查看网络连接
netstat -tulpn | grep python
```

## 🔄 更新和维护

### 更新应用
1. 备份当前配置：
   ```bash
   cp /volume1/python_apps/synology_app/config.json /volume1/python_apps/synology_app/config.json.backup
   ```

2. 停止应用：
   ```bash
   /volume1/python_apps/synology_app/stop_app.sh
   ```

3. 替换应用文件：
   ```bash
   # 备份旧版本
   mv synology_app.py synology_app.py.old
   
   # 上传新版本
   # ...
   ```

4. 启动应用：
   ```bash
   /volume1/python_apps/synology_app/start_app.sh
   ```

### 备份配置
```bash
# 创建备份脚本
cat > /volume1/python_apps/synology_app/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/volume1/backups/synology_app"
APP_DIR="/volume1/python_apps/synology_app"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# 备份配置和日志
tar -czf "$BACKUP_DIR/synology_app_backup_$DATE.tar.gz" \
    -C "$APP_DIR" \
    config.json logs/

echo "备份完成: $BACKUP_DIR/synology_app_backup_$DATE.tar.gz"
EOF

chmod +x /volume1/python_apps/synology_app/backup.sh
```

## 📞 技术支持

### 获取帮助
1. 查看应用日志文件
2. 检查系统资源使用情况
3. 验证网络连接
4. 确认配置文件格式

### 联系方式
- 查看 `README.md` 获取详细使用说明
- 检查 `logs/app.log` 获取错误信息
- 运行 `python3 synology_app.py` 查看实时输出

---

**安装愉快！** 🎉