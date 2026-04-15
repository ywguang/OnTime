"""
打卡提醒系统配置文件
所有参数都可以在这里自定义修改
"""

import os
import sys

# 获取项目根目录
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后的环境
    # exe 所在目录
    exe_dir = os.path.dirname(sys.executable)
    # 检查是否存在 _internal 目录（PyInstaller 目录模式）
    internal_dir = os.path.join(exe_dir, '_internal')
    if os.path.exists(internal_dir):
        # 资源文件在 _internal 目录下
        PROJECT_ROOT = internal_dir
    else:
        # 单文件模式或资源在 exe 同目录
        PROJECT_ROOT = exe_dir
else:
    # 开发环境
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ========== 时间配置 ==========
WORK_START_TIME = "09:00"        # 上班时间
WORK_END_TIME = "15:45"          # 下班时间
REMIND_ADVANCE_MINUTES = 5       # 提前提醒分钟数
REMIND_INTERVAL_MINUTES = 3      # 重复提醒间隔（分钟）
MAX_REMIND_COUNT = 3             # 最大提醒次数（超过此次数后停止提醒）
ABSOLUTE_MAX_REMIND_COUNT = 5    # 绝对最大提醒次数（硬性限制，防止无限提醒）

# ========== 工作日配置 ==========
SKIP_WEEKEND = True              # 是否跳过周末（周六日不提醒）

# 2026年中国法定节假日列表（需要根据实际放假安排调整）
# 格式：YYYY-MM-DD
HOLIDAYS_2026 = [
    # 元旦
    "2026-01-01",  # 星期四
    "2026-01-02",  # 星期五
    "2026-01-03",  # 星期六
    
    # 春节（预计）
    "2026-02-15",  # 星期日
    "2026-02-16",  # 星期一
    "2026-02-17",  # 星期二
    "2026-02-18",  # 星期三
    "2026-02-19",  # 星期四
    "2026-02-20",  # 星期五
    "2026-02-21",  # 星期六
    
    # 清明节（预计）
    "2026-04-04",  # 星期六
    "2026-04-05",  # 星期日
    "2026-04-06",  # 星期一
    
    # 劳动节（预计）
    "2026-05-01",  # 星期五
    "2026-05-02",  # 星期六
    "2026-05-03",  # 星期日
    
    # 端午节（预计）
    "2026-06-19",  # 星期五
    "2026-06-20",  # 星期六
    "2026-06-21",  # 星期日
    
    # 中秋节（预计）
    "2026-09-25",  # 星期五
    "2026-09-26",  # 星期六
    "2026-09-27",  # 星期日
    
    # 国庆节（预计）
    "2026-10-01",  # 星期四
    "2026-10-02",  # 星期五
    "2026-10-03",  # 星期六
    "2026-10-04",  # 星期日
    "2026-10-05",  # 星期一
    "2026-10-06",  # 星期二
    "2026-10-07",  # 星期三
]

# 合并所有节假日（方便后续扩展多年）
HOLIDAYS = HOLIDAYS_2026

# ========== 弹窗样式配置 ==========
BACKGROUND_IMAGE = os.path.join(PROJECT_ROOT, "assets", "images", "background.jpg")  # 背景图片路径
TITLE_TEXT = "⏰ 打卡提醒"                   # 标题文字
MESSAGE_TEXT_WORK = "该打卡了！\n请拿出手机打开钉钉打卡"      # 上班提醒文字（默认，会被随机文案覆盖）
MESSAGE_TEXT_OFF = "该打卡了！\n请拿出手机打开钉钉打卡"       # 下班提醒文字（默认，会被随机文案覆盖）
BUTTON_CONFIRM_TEXT = "✓ 我已打卡"          # 确认按钮文字
BUTTON_LATER_TEXT = "⏱ 稍后提醒"            # 稍后按钮文字
WINDOW_ALPHA = 1.0                           # 窗口透明度（0.0-1.0，1.0为完全不透明）

# ========== 随机文案配置 ==========
# 启用随机文案（True=启用，False=使用上面的固定文案）
ENABLE_RANDOM_MESSAGES = True

# 上班打卡文案库（每次随机选择一条）
WORK_START_MESSAGES = [
    "该打卡了！请拿出手机打开钉钉打卡",
    "少年，打卡的时间到了！",
    "叮！您的上班打卡提醒已送达～",
    "美好的一天从打卡开始！",
    "温馨提醒：上班打卡时间到啦",
    "此乃打卡之时，速速行动！",
    "天命之子，岂能忘记打卡？",
    "老板在看着你哦～快去打卡！",
    "打卡不积极，思想有问题 😏",
    "全勤奖在向你招手！快打卡！",
]

# 下班打卡文案库（每次随机选择一条）
WORK_END_MESSAGES = [
    "该打卡了！请拿出手机打开钉钉打卡",
    "下班啦！打完卡就可以回家咯～",
    "辛苦一天，记得打卡再走哦",
    "自由的气息在召唤！快打卡！",
    "夕阳西下，打卡回家～",
    "今日工作已结束，打卡撤退！",
    "回家的诱惑：打完卡就能走啦",
    "坚持住！打完这最后一次卡！",
    "解放倒计时：先打卡！",
    "收工大吉！别忘了打卡哦",
]

# ========== 时间段图片配置 ==========
# 启用时间段图片切换（True=根据时间自动选择，False=使用上面固定的BACKGROUND_IMAGE）
ENABLE_TIME_BASED_IMAGES = True

# 时间段定义（24小时制）
TIME_PERIODS = {
    "morning": {"start": 6, "end": 9},     # 早晨 6:00-9:00
    "daytime": {"start": 9, "end": 17},    # 白天 9:00-17:00
    "evening": {"start": 17, "end": 19},   # 傍晚 17:00-19:00
    "night": {"start": 19, "end": 6},      # 夜晚 19:00-次日6:00
}

# 各时间段的图片文件夹（相对于项目根目录）
IMAGE_FOLDERS = {
    "morning": os.path.join(PROJECT_ROOT, "assets", "images", "morning"),     # 早晨主题图片
    "daytime": os.path.join(PROJECT_ROOT, "assets", "images", "daytime"),     # 白天主题图片
    "evening": os.path.join(PROJECT_ROOT, "assets", "images", "evening"),     # 傍晚主题图片
    "night": os.path.join(PROJECT_ROOT, "assets", "images", "night"),         # 夜晚主题图片
}

# ========== 日志配置 ==========
LOG_DIR = os.path.join(PROJECT_ROOT, "assets", "logs")                           # 日志文件夹路径
LOG_FILE = os.path.join(PROJECT_ROOT, "assets", "logs", "remind.log")           # 日志文件路径
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # 日志格式
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"        # 日期格式

# ========== 其他配置 ==========
APP_NAME = "打卡提醒助手"                     # 应用程序名称
VERSION = "1.0.0"                            # 版本号
