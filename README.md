# OnTime - 打卡提醒助手

一款专为上班族设计的智能打卡提醒工具，支持上下班提醒、多次提醒、稍后提醒等功能，采用美观的毛玻璃圆角弹窗设计，支持根据时间段自动切换背景图片。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 功能特性

### 核心功能
- 🔔 **智能提醒**: 在设定的上下班时间自动弹出全屏提醒
- 🔄 **多次提醒**: 支持多次提醒，防止错过打卡时间
- ⏱️ **稍后提醒**: 点击"稍后提醒"后，按设定间隔再次提醒
- 📅 **工作日判断**: 自动跳过周末和法定节假日
- 🖼️ **动态背景**: 根据时间段自动切换背景图片（早晨/白天/傍晚/夜晚）

### 界面特性
- 🎨 **毛玻璃效果**: 圆角毛玻璃弹窗设计，美观现代
- 📝 **随机文案**: 每次提醒显示不同的趣味文案
- 🎭 **时间段主题**: 支持4个时间段的不同主题图片
- 🖥️ **系统托盘**: 最小化到系统托盘，不占用任务栏
- ⚙️ **图形配置**: 可视化配置界面，无需修改代码

### 实用功能
- 📊 **日志记录**: 完整记录提醒历史、打卡时间、提醒次数
- 🚀 **开机自启**: 支持设置开机自动启动
- 🧪 **测试弹窗**: 随时测试提醒效果
- 📋 **查看日志**: 一键打开日志文件

## 📦 安装要求

### 系统要求
- **操作系统**: Windows 10/11
- **Python版本**: 3.8 或更高

### 依赖安装

```bash
pip install -r requirements.txt
```

依赖包：
- `Pillow>=9.0.0` - 图片处理
- `schedule>=1.2.0` - 定时任务
- `pystray>=0.19.0` - 系统托盘

## 🚀 快速开始

### 1. 克隆或下载项目

```bash
git clone https://github.com/ywguang/OnTime.git
cd OnTime
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 准备背景图片（可选）

将喜欢的图片放入对应文件夹：

```
assets/images/
├── morning/     # 早晨 6:00-9:00
├── daytime/     # 白天 9:00-17:00
├── evening/     # 傍晚 17:00-19:00
├── night/       # 夜晚 19:00-次日6:00
└── background.jpg  # 默认背景图
```

### 4. 运行程序

```bash
python main.py
```

程序启动后会显示在系统托盘，到达设定时间自动弹出提醒。

## ⚙️ 配置说明

### 配置方式

#### 方式一：图形界面（推荐）

1. 右键系统托盘图标
2. 选择"打开配置"
3. 修改参数后点击"保存配置"

#### 方式二：配置文件

编辑 `config/user_config.json`：

```json
{
  "WORK_START_TIME": "09:00",
  "WORK_END_TIME": "17:30",
  "REMIND_ADVANCE_MINUTES": 5,
  "REMIND_INTERVAL_MINUTES": 3,
  "MAX_REMIND_COUNT": 3,
  "SKIP_WEEKEND": true,
  "ENABLE_RANDOM_MESSAGES": true,
  "ENABLE_TIME_BASED_IMAGES": true
}
```

### 配置项详解

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `WORK_START_TIME` | string | "09:00" | 上班时间（HH:MM格式） |
| `WORK_END_TIME` | string | "17:30" | 下班时间（HH:MM格式） |
| `REMIND_ADVANCE_MINUTES` | int | 5 | 提前提醒分钟数 |
| `REMIND_INTERVAL_MINUTES` | int | 3 | 稍后提醒间隔分钟数 |
| `MAX_REMIND_COUNT` | int | 3 | 建议最大提醒次数 |
| `ABSOLUTE_MAX_REMIND_COUNT` | int | 5 | 绝对最大提醒次数（硬性限制） |
| `SKIP_WEEKEND` | bool | true | 是否跳过周末 |
| `ENABLE_RANDOM_MESSAGES` | bool | true | 是否启用随机文案 |
| `ENABLE_TIME_BASED_IMAGES` | bool | true | 是否启用时间段图片切换 |
| `WINDOW_ALPHA` | float | 1.0 | 窗口透明度（0.0-1.0） |

## 📁 项目结构

```
OnTime/
├── main.py                 # 主入口程序
├── requirements.txt        # 依赖包列表
├── README.md               # 项目说明文档
├── 使用指南.txt             # 详细使用指南
│
├── config/                 # 配置模块
│   ├── __init__.py
│   ├── default_config.py   # 默认配置
│   └── user_config.json    # 用户配置文件
│
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── notifier.py         # 弹窗通知模块
│   ├── scheduler.py        # 定时任务调度
│   └── text_manager.py     # 文案管理器
│
├── ui/                     # 界面模块
│   ├── __init__.py
│   ├── config_ui.py        # 配置界面
│   └── tray_icon.py        # 托盘图标
│
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── image_manager.py    # 图片管理器
│   ├── logger.py           # 日志记录
│   └── path_helper.py      # 路径助手
│
└── assets/                 # 资源文件
    ├── images/             # 背景图片
    │   ├── morning/        # 早晨主题 (6:00-9:00)
    │   ├── daytime/        # 白天主题 (9:00-17:00)
    │   ├── evening/        # 傍晚主题 (17:00-19:00)
    │   ├── night/          # 夜晚主题 (19:00-次日6:00)
    │   └── background.jpg  # 默认背景
    └── logs/               # 日志文件
        └── remind.log
```

## 🎨 自定义功能

### 自定义背景图片

#### 方法一：时间段自动切换（推荐）

1. 将图片按时间段分类放入对应文件夹
2. 启用 `ENABLE_TIME_BASED_IMAGES: true`
3. 程序自动根据当前时间选择主题

#### 方法二：固定背景图

1. 将图片放入 `assets/images/background.jpg`
2. 设置 `ENABLE_TIME_BASED_IMAGES: false`

### 自定义提醒文案

编辑 `config/user_config.json`：

```json
{
  "WORK_START_MESSAGES": [
    "该打卡了！请拿出手机打开钉钉打卡",
    "少年，打卡的时间到了！",
    "叮！您的上班打卡提醒已送达～"
  ],
  "WORK_END_MESSAGES": [
    "下班啦！打完卡就可以回家咯～",
    "辛苦一天，记得打卡再走哦",
    "自由的气息在召唤！快打卡！"
  ]
}
```

### 设置开机自启动

#### 方法一：配置界面设置

1. 右键托盘图标 → 打开配置
2. 勾选"开机自动启动"
3. 保存配置

#### 方法二：手动设置

1. 按 `Win + R`，输入 `shell:startup`，回车
2. 创建快捷方式指向程序

## 📝 日志查看

程序在 `assets/logs/remind.log` 中记录所有操作：

```
2026-04-15 08:55:00 - INFO - ==================================================
2026-04-15 08:55:00 - INFO - 打卡提醒助手 v1.0.0 启动
2026-04-15 08:55:00 - INFO - ==================================================
2026-04-15 08:55:00 - INFO - 图片管理器初始化完成
2026-04-15 08:55:00 - INFO - 时间段图片切换已启用
2026-04-15 08:55:00 - INFO - 文案管理器初始化完成
2026-04-15 08:55:00 - INFO - 随机文案已启用 - 上班文案10条，下班文案10条
2026-04-15 08:55:00 - INFO - 启动定时任务调度器
2026-04-15 08:55:00 - INFO - [work_start] 已设置每日 08:55 提醒
2026-04-15 08:55:00 - INFO - [work_end] 已设置每日 17:25 提醒
```

查看日志：
- 右键托盘图标 → 查看日志
- 或直接打开 `assets/logs/remind.log`

## ❓ 常见问题

### Q: 弹窗没有显示？

**A:** 请检查：
1. 程序是否正在运行（检查托盘图标）
2. 查看日志文件是否有错误
3. 确认今天是否为工作日（周末/节假日会跳过）
4. 检查提醒时间设置是否正确

### Q: 如何测试提醒功能？

**A:** 右键托盘图标 → 测试弹窗，即可立即看到提醒效果。

### Q: 背景图片显示异常？

**A:** 检查：
- 图片路径是否正确
- 图片格式是否支持（JPG、PNG、BMP、GIF、WebP）
- 程序是否有读取权限

### Q: 配置修改后没有生效？

**A:** 配置修改后需要**重启程序**才能生效。保存配置后退出程序，重新运行即可。

### Q: 如何停止程序？

**A:** 
- 方法1：右键托盘图标 → 退出程序
- 方法2：在命令行窗口按 `Ctrl+C`

### Q: 节假日如何更新？

**A:** 每年需要手动更新 `config/default_config.py` 中的 `HOLIDAYS` 列表，根据国务院发布的放假安排调整。

## 🔧 开发说明

### 添加新的提醒类型

编辑 `core/scheduler.py`：

```python
def start_scheduler():
    # 添加新的提醒类型
    schedule_daily_reminder("lunch", "12:00")  # 午餐提醒
```

### 自定义弹窗样式

编辑 `core/notifier.py` 中的 `RemindWindow` 类：

```python
def _create_glass_effect(self):
    # 自定义毛玻璃效果
    pass

def _create_rounded_buttons_v2(self, card_x, card_y, card_width, card_height, btn_y):
    # 自定义按钮样式
    pass
```

### 添加新的时间段

编辑 `config/default_config.py`：

```python
TIME_PERIODS = {
    "morning": {"start": 6, "end": 9},
    "daytime": {"start": 9, "end": 17},
    "evening": {"start": 17, "end": 19},
    "night": {"start": 19, "end": 6},
    "midnight": {"start": 0, "end": 6},  # 新增
}

IMAGE_FOLDERS = {
    "morning": os.path.join(PROJECT_ROOT, "assets", "images", "morning"),
    "daytime": os.path.join(PROJECT_ROOT, "assets", "images", "daytime"),
    "evening": os.path.join(PROJECT_ROOT, "assets", "images", "evening"),
    "night": os.path.join(PROJECT_ROOT, "assets", "images", "night"),
    "midnight": os.path.join(PROJECT_ROOT, "assets", "images", "midnight"),  # 新增
}
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 开源协议

本项目基于 [MIT](LICENSE) 协议开源。

## 🙏 致谢

- [Pillow](https://python-pillow.org/) - 强大的图片处理库
- [schedule](https://github.com/dbader/schedule) - 轻量级定时任务库
- [pystray](https://github.com/moses-palmer/pystray) - 跨平台系统托盘库

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 [Issue](https://github.com/ywguang/OnTime/issues)
- GitHub: [ywguang](https://github.com/ywguang)

---

**如果觉得这个项目对你有帮助，欢迎给个 Star ⭐️ 支持一下！**
