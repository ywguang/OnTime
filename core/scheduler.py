"""
定时任务调度模块
负责计算提醒时间、判断工作日、管理多次提醒逻辑
"""

import threading
import time
from datetime import datetime, timedelta
from config import (
    WORK_START_TIME, WORK_END_TIME, REMIND_ADVANCE_MINUTES,
    REMIND_INTERVAL_MINUTES, MAX_REMIND_COUNT, ABSOLUTE_MAX_REMIND_COUNT,
    SKIP_WEEKEND, HOLIDAYS
)
from utils.logger import logger, log_remind, log_confirm, log_skip
from core.notifier import show_reminder


class RemindState:
    """提醒状态管理器"""
    
    def __init__(self):
        self.remainder_count = {}  # 记录每种提醒类型的当前次数 {remind_type: count}
        self.active_reminders = {}  # 记录正在进行的提醒 {remind_type: Timer对象}
        
    def get_count(self, remind_type):
        """获取当前提醒次数"""
        return self.remainder_count.get(remind_type, 0)
    
    def increment_count(self, remind_type):
        """增加提醒次数"""
        if remind_type not in self.remainder_count:
            self.remainder_count[remind_type] = 0
        self.remainder_count[remind_type] += 1
        return self.remainder_count[remind_type]
    
    def reset_count(self, remind_type):
        """重置提醒次数"""
        self.remainder_count[remind_type] = 0
    
    def can_remind(self, remind_type):
        """检查是否可以继续提醒"""
        count = self.get_count(remind_type)
        return count < ABSOLUTE_MAX_REMIND_COUNT
    
    def cancel_pending(self, remind_type):
        """取消待执行的提醒"""
        if remind_type in self.active_reminders:
            timer = self.active_reminders[remind_type]
            timer.cancel()
            del self.active_reminders[remind_type]


# 全局提醒状态
remind_state = RemindState()


def is_workday(date=None):
    """
    判断指定日期是否为工作日
    
    Args:
        date (datetime): 要判断的日期，默认为今天
        
    Returns:
        bool: True为工作日，False为非工作日
    """
    if date is None:
        date = datetime.now()
    
    # 检查是否为周末
    if SKIP_WEEKEND and date.weekday() >= 5:  # 5=周六, 6=周日
        return False
    
    # 检查是否为法定节假日
    date_str = date.strftime("%Y-%m-%d")
    if date_str in HOLIDAYS:
        return False
    
    return True


def calculate_remind_time(base_time_str, advance_minutes=0):
    """
    计算提醒时间
    
    Args:
        base_time_str (str): 基础时间字符串（格式：HH:MM）
        advance_minutes (int): 提前分钟数
        
    Returns:
        str: 提醒时间字符串（格式：HH:MM）
    """
    # 解析时间
    hour, minute = map(int, base_time_str.split(':'))
    
    # 计算提前的时间
    remind_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    remind_time = remind_time - timedelta(minutes=advance_minutes)
    
    # 返回格式化时间
    return remind_time.strftime("%H:%M")


def schedule_later_remind(remind_type):
    """
    调度稍后提醒
    
    Args:
        remind_type (str): 提醒类型
        
    Returns:
        int: 下次提醒的间隔分钟数
    """
    current_count = remind_state.get_count(remind_type)
    
    # 检查是否超过最大次数
    if current_count >= ABSOLUTE_MAX_REMIND_COUNT:
        logger.info(f"[{remind_type}] 已达到绝对最大提醒次数({ABSOLUTE_MAX_REMIND_COUNT})，停止提醒")
        remind_state.reset_count(remind_type)
        return 0
    
    # 增加提醒次数
    new_count = remind_state.increment_count(remind_type)
    
    # 检查是否超过建议最大次数
    if new_count > MAX_REMIND_COUNT:
        logger.warning(f"[{remind_type}] 已超过建议最大提醒次数({MAX_REMIND_COUNT})，但仍会继续提醒直到{ABSOLUTE_MAX_REMIND_COUNT}次")
    
    # 计算延迟时间（秒）
    delay_seconds = REMIND_INTERVAL_MINUTES * 60
    
    # 计算下次提醒的具体时间
    from datetime import datetime, timedelta
    next_remind_time = datetime.now() + timedelta(minutes=REMIND_INTERVAL_MINUTES)
    next_remind_time_str = next_remind_time.strftime("%H:%M")
    
    logger.info(f"[{remind_type}] 将在{REMIND_INTERVAL_MINUTES}分钟后({next_remind_time_str})进行第{new_count}次提醒")
    log_remind(remind_type, new_count, f"稍后提醒，{REMIND_INTERVAL_MINUTES}分钟后({next_remind_time_str})")
    
    # 创建定时器
    timer = threading.Timer(delay_seconds, trigger_reminder, args=[remind_type])
    remind_state.active_reminders[remind_type] = timer
    timer.start()
    
    return REMIND_INTERVAL_MINUTES


def trigger_reminder(remind_type):
    """
    触发提醒
    
    Args:
        remind_type (str): 提醒类型（"work_start" 或 "work_end"）
    """
    logger.info(f"[{remind_type}] 开始触发提醒流程")
    
    # 检查今天是否为工作日
    if not is_workday():
        logger.info(f"[{remind_type}] 今天不是工作日，跳过提醒")
        log_skip("非工作日")
        remind_state.reset_count(remind_type)
        return
    
    # 检查是否可以继续提醒
    if not remind_state.can_remind(remind_type):
        logger.info(f"[{remind_type}] 已达到最大提醒次数，停止提醒")
        remind_state.reset_count(remind_type)
        return
    
    # 增加提醒次数
    current_count = remind_state.increment_count(remind_type)
    
    # 记录日志
    log_remind(remind_type, current_count, "触发提醒")
    logger.info(f"[{remind_type}] 第{current_count}次提醒，准备显示窗口")
    
    # 定义回调函数
    def on_confirm():
        """用户确认打卡"""
        confirm_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_confirm(remind_type, current_count, confirm_time)
        remind_state.reset_count(remind_type)
        logger.info(f"[{remind_type}] 打卡流程完成")
    
    def on_later():
        """用户选择稍后提醒"""
        logger.info(f"[{remind_type}] 用户选择稍后提醒")
        schedule_later_remind(remind_type)
    
    try:
        # 显示提醒窗口（在新线程中，避免阻塞）
        logger.info(f"[{remind_type}] 正在创建提醒窗口线程...")
        reminder_thread = threading.Thread(
            target=show_reminder,
            kwargs={
                "remind_type": remind_type,
                "on_confirm": on_confirm,
                "on_later": on_later
            },
            daemon=True
        )
        reminder_thread.start()
        logger.info(f"[{remind_type}] 提醒窗口线程已启动")
        
        # 等待线程完成（可选，用于调试）
        # reminder_thread.join(timeout=60)
        
    except Exception as e:
        logger.error(f"[{remind_type}] 显示提醒窗口失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def schedule_daily_reminder(remind_type, base_time_str):
    """
    调度每日定时提醒
    
    Args:
        remind_type (str): 提醒类型（"work_start" 或 "work_end"）
        base_time_str (str): 基础时间（格式：HH:MM）
    """
    import schedule
    
    # 计算提醒时间（考虑提前量）
    if remind_type == "work_start":
        remind_time = calculate_remind_time(base_time_str, REMIND_ADVANCE_MINUTES)
    else:
        remind_time = calculate_remind_time(base_time_str, REMIND_ADVANCE_MINUTES)
    
    logger.info(f"[{remind_type}] 已设置每日 {remind_time} 提醒")
    
    # 设置定时任务
    schedule.every().day.at(remind_time).do(trigger_reminder, remind_type)


def start_scheduler():
    """启动调度器"""
    import schedule
    
    logger.info("启动定时任务调度器")
    
    # 设置上班提醒
    schedule_daily_reminder("work_start", WORK_START_TIME)
    
    # 设置下班提醒
    schedule_daily_reminder("work_end", WORK_END_TIME)
    
    # 运行调度器（在主线程中持续运行）
    logger.info("调度器正在运行...")
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler_in_background():
    """在后台线程启动调度器"""
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("调度器已在后台启动")
    return scheduler_thread


if __name__ == "__main__":
    # 测试代码
    print("测试工作日判断:")
    test_dates = [
        datetime(2026, 1, 6),   # 周二
        datetime(2026, 1, 10),  # 周六
        datetime(2026, 1, 1),   # 元旦
    ]
    
    for date in test_dates:
        workday = is_workday(date)
        print(f"{date.strftime('%Y-%m-%d %A')}: {'工作日' if workday else '休息日'}")
    
    print("\n测试提醒时间计算:")
    print(f"上班时间 {WORK_START_TIME}, 提前{REMIND_ADVANCE_MINUTES}分钟提醒: {calculate_remind_time(WORK_START_TIME, REMIND_ADVANCE_MINUTES)}")
    print(f"下班时间 {WORK_END_TIME}, 提前{REMIND_ADVANCE_MINUTES}分钟提醒: {calculate_remind_time(WORK_END_TIME, REMIND_ADVANCE_MINUTES)}")
