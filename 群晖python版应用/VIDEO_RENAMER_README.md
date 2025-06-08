# 智能影视文件重命名工具

## 📖 项目简介

这是一个跨平台的智能影视文件重命名工具，专为群晖Video Station优化，同时支持Windows和macOS系统。

### 🌟 主要特点

- **🔍 智能识别**: 自动提取影片标题、年份、季集、分辨率等信息
- **🎯 精准匹配**: 支持多种文件命名格式和正则表达式规则
- **👀 预览模式**: Dry-run功能，重命名前可预览结果
- **🛡️ 安全保护**: 自动备份、批量限制、文件名验证
- **🔧 灵活配置**: 多种重命名模板，支持自定义
- **🏠 群晖优化**: 专为群晖Video Station设计的命名规范
- **💻 跨平台**: 支持Windows、macOS、Linux、群晖NAS

## 🚀 快速开始

### 1. 运行程序

```bash
# 进入工具目录
cd 群晖python版应用

# 运行重命名工具
python3 video_renamer.py
```

### 2. 首次运行

首次运行时，程序会：
1. 自动创建配置文件 `video_renamer_config.json`
2. 创建日志目录 `logs/`
3. 显示配置说明和使用提示
4. 进入交互式界面

### 3. 基本操作流程

1. **选择操作**: 从主菜单选择功能
2. **扫描目录**: 输入要处理的视频文件目录
3. **预览结果**: 查看重命名预览，确认无误
4. **执行重命名**: 确认后执行实际重命名操作

## 📋 功能详解

### 🔍 智能信息提取

工具能够从文件名中自动提取以下信息：

#### 电影信息
- **标题**: 影片名称
- **年份**: 发行年份
- **分辨率**: 4K、1080p、720p等
- **画质**: BluRay、WEBRip、HDTV等
- **来源**: Netflix、Amazon等
- **编码**: x264、x265、HEVC等
- **音频**: DTS、AC3、AAC等
- **制作组**: 发布组信息

#### 电视剧信息
- **剧名**: 电视剧名称
- **季数**: Season信息
- **集数**: Episode信息
- **其他**: 分辨率、画质等同电影

### 📝 支持的文件格式

```
视频格式: .mp4, .mkv, .avi, .mov, .wmv, .flv, .webm, .m4v, 
         .3gp, .ts, .mts, .m2ts, .rmvb, .rm, .asf, .f4v, .vob

字幕格式: .srt, .ass, .ssa, .sub, .idx, .vtt
```

### 🎨 重命名模板

#### 电影模板

1. **群晖默认** (推荐)
   ```
   电影名 (2023) [1080p] [BluRay].mp4
   ```

2. **Plex格式**
   ```
   电影名 (2023).mp4
   ```

3. **详细格式**
   ```
   电影名 (2023) [1080p] [BluRay] [x264] [DTS].mp4
   ```

4. **简单格式**
   ```
   电影名 (2023).mp4
   ```

#### 电视剧模板

1. **群晖默认** (推荐)
   ```
   剧名 S01E01 [1080p] [WEBRip].mp4
   ```

2. **Plex格式**
   ```
   剧名 - S01E01.mp4
   ```

3. **详细格式**
   ```
   剧名 S01E01 [1080p] [Netflix] [x264].mp4
   ```

4. **中文格式**
   ```
   剧名 - 第1季第01集.mp4
   ```

## ⚙️ 配置文件详解

配置文件 `video_renamer_config.json` 包含以下主要配置节：

### 📱 应用信息 (app_info)
```json
{
    "name": "智能影视文件重命名工具",
    "version": "1.0.0",
    "supported_os": ["Windows", "macOS", "Linux", "Synology"]
}
```

### 🎬 支持格式 (supported_formats)
```json
{
    "video_extensions": [".mp4", ".mkv", ".avi", ...],
    "subtitle_extensions": [".srt", ".ass", ".ssa", ...]
}
```

### 📝 命名模板 (naming_templates)
```json
{
    "movie_templates": {
        "synology_default": "{title} ({year}) [{resolution}] [{quality}].{ext}",
        "plex_format": "{title} ({year}).{ext}",
        ...
    },
    "tv_templates": {
        "synology_default": "{title} S{season:02d}E{episode:02d} [{resolution}] [{quality}].{ext}",
        ...
    }
}
```

### 🔍 提取规则 (extraction_rules)

#### 电影模式正则表达式
```json
{
    "movie_patterns": [
        {
            "name": "标准电影格式",
            "pattern": "^(.+?)[\\.\s]+(\\d{4})[\\.\s]*(.*)$",
            "description": "匹配：电影名.2023.1080p.BluRay.x264"
        }
    ]
}
```

#### 电视剧模式正则表达式
```json
{
    "tv_patterns": [
        {
            "name": "标准剧集格式",
            "pattern": "^(.+?)[\\.\s]+[Ss](\\d{1,2})[Ee](\\d{1,2})[\\.\s]*(.*)$",
            "description": "匹配：剧名.S01E01.1080p"
        }
    ]
}
```

### 🏠 群晖设置 (synology_settings)
```json
{
    "video_station_path": "/volume1/video",
    "movie_folder": "Movies",
    "tv_folder": "TV Shows",
    "create_season_folders": true,
    "season_folder_format": "Season {season:02d}"
}
```

### 🛡️ 安全设置 (safety_settings)
```json
{
    "max_files_per_batch": 1000,
    "confirm_before_rename": true,
    "create_undo_log": true,
    "forbidden_characters": ["<", ">", ":", "\"", "|", "?", "*"],
    "max_filename_length": 255
}
```

## 🎯 使用场景示例

### 场景1：整理下载的电影

**原始文件名:**
```
The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv
Inception.2010.720p.WEBRip.x264.AAC-YTS.mp4
```

**重命名后 (群晖模板):**
```
The Matrix (1999) [1080p] [BluRay].mkv
Inception (2010) [720p] [WEBRip].mp4
```

### 场景2：整理电视剧集

**原始文件名:**
```
Game.of.Thrones.S01E01.1080p.BluRay.x264-DEMAND.mkv
Breaking.Bad.S02E05.720p.HDTV.x264-CTU.avi
```

**重命名后 (群晖模板):**
```
Game of Thrones S01E01 [1080p] [BluRay].mkv
Breaking Bad S02E05 [720p] [HDTV].avi
```

### 场景3：中文影视内容

**原始文件名:**
```
流浪地球.2019.1080p.WEBRip.x264.mkv
庆余年.第一季.第01集.1080p.WEB-DL.x264.mp4
```

**重命名后:**
```
流浪地球 (2019) [1080p] [WEBRip].mkv
庆余年 S01E01 [1080p] [WEB-DL].mp4
```

## 🔧 高级功能

### 1. 自定义正则表达式

可以在配置文件中添加自定义的提取规则：

```json
{
    "name": "自定义格式",
    "pattern": "你的正则表达式",
    "groups": {"title": 1, "year": 2, "extra": 3},
    "description": "规则描述"
}
```

### 2. 批量处理

- 支持递归扫描子目录
- 自动跳过已正确命名的文件
- 批量大小限制保护

### 3. 备份功能

- 重命名前自动备份原文件
- 备份目录按时间戳命名
- 支持撤销操作

### 4. 日志记录

- 详细的操作日志
- 错误信息记录
- 支持不同日志级别

## 🏠 群晖NAS专用功能

### Video Station优化

1. **标准目录结构**
   ```
   /volume1/video/
   ├── Movies/
   │   ├── 电影名 (2023) [1080p] [BluRay].mp4
   │   └── ...
   └── TV Shows/
       ├── 剧名/
       │   ├── Season 01/
       │   │   ├── 剧名 S01E01 [1080p] [WEBRip].mp4
       │   │   └── ...
       │   └── Season 02/
       └── ...
   ```

2. **元数据保留**
   - 自动保留 .nfo 文件
   - 保留海报和缩略图
   - 维护目录结构

3. **权限设置**
   - 自动设置正确的文件权限
   - 支持群晖用户组

## 💻 跨平台使用

### Windows系统

```cmd
# 使用命令提示符
cd "群晖python版应用"
python video_renamer.py

# 或使用PowerShell
cd "群晖python版应用"
python3 video_renamer.py
```

### macOS系统

```bash
# 使用终端
cd "群晖python版应用"
python3 video_renamer.py
```

### 群晖NAS

```bash
# SSH连接到群晖
ssh admin@your-synology-ip

# 进入应用目录
cd /volume1/python_apps/群晖python版应用

# 运行程序
python3 video_renamer.py
```

## 🛠️ 故障排除

### 常见问题

#### 1. 无法识别文件名格式

**解决方案:**
- 检查文件名是否符合常见格式
- 在配置文件中添加自定义正则表达式
- 查看日志文件获取详细信息

#### 2. 重命名后文件无法播放

**解决方案:**
- 检查文件扩展名是否正确
- 确认文件没有损坏
- 验证播放器支持该格式

#### 3. 权限不足错误

**解决方案:**
```bash
# Linux/macOS
chmod 755 video_renamer.py
sudo python3 video_renamer.py

# 群晖
sudo python3 video_renamer.py
```

#### 4. 中文文件名乱码

**解决方案:**
- 确保系统支持UTF-8编码
- 检查终端编码设置
- 在配置文件中设置正确的编码

### 日志分析

查看日志文件获取详细错误信息：

```bash
# 查看最新日志
tail -f logs/video_renamer.log

# 搜索错误信息
grep "ERROR" logs/video_renamer.log
```

## 📈 性能优化

### 大量文件处理

1. **分批处理**: 设置合理的批处理大小
2. **并行处理**: 对于大量文件，可以分目录并行处理
3. **内存管理**: 避免一次性加载过多文件信息

### 网络存储优化

1. **本地缓存**: 先下载到本地处理，再上传
2. **增量处理**: 只处理新增或修改的文件
3. **断点续传**: 支持中断后继续处理

## 🔄 更新和维护

### 配置备份

```bash
# 备份配置文件
cp video_renamer_config.json video_renamer_config.json.backup

# 备份日志
tar -czf logs_backup.tar.gz logs/
```

### 版本更新

1. 备份当前配置和日志
2. 替换主程序文件
3. 检查配置文件兼容性
4. 测试基本功能

## 📞 技术支持

### 获取帮助

1. 查看程序内置帮助 (选项5)
2. 检查日志文件错误信息
3. 验证配置文件格式
4. 测试正则表达式规则

### 反馈问题

提供以下信息有助于问题诊断：
- 操作系统版本
- Python版本
- 错误日志内容
- 问题文件名示例
- 期望的重命名结果

---

**祝你使用愉快！** 🎉

> 💡 **小贴士**: 建议首次使用时先在测试目录中尝试，熟悉功能后再处理重要文件。