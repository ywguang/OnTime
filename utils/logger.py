"""
日志记录模块
负责记录提醒时间、确认时间、提醒次数等信息
"""

import logging
import os
from config import LOG_DIR, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT


def setup_logger():
    """
    配置并返回logger实例
    
    Returns:
        logging.Logger: 配置好的logger对象
    """
    # 创建日志目录（如果不存在）
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # 创建logger
    logger = logging.getLogger("DingdingRemind")
    logger.setLevel(logging.INFO)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    # 创建文件handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台handler（可选，调试时使用）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置格式
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# 创建全局logger实例
logger = setup_logger()


def log_remind(remind_type, remind_count, message=""):
    """
    记录提醒日志
    
    Args:
        remind_type (str): 提醒类型（"work_start" 或 "work_end"）
        remind_count (int): 当前提醒次数
        message (str): 附加消息
    """
    type_text = "上班打卡" if remind_type == "work_start" else "下班打卡"
    log_msg = f"[{type_text}] 第{remind_count}次提醒 - {message}"
    logger.info(log_msg)


def log_confirm(remind_type, remind_count, confirm_time):
    """
    记录确认打卡日志
    
    Args:
        remind_type (str): 提醒类型（"work_start" 或 "work_end"）
        remind_count (int): 确认时的提醒次数
        confirm_time (str): 确认时间字符串
    """
    type_text = "上班打卡" if remind_type == "work_start" else "下班打卡"
    log_msg = f"[{type_text}] 用户已确认打卡 - 第{remind_count}次提醒时确认 - 确认时间: {confirm_time}"
    logger.info(log_msg)


def log_skip(reason):
    """
    记录跳过提醒的日志
    
    Args:
        reason (str): 跳过原因
    """
    logger.info(f"[跳过提醒] 原因: {reason}")


def log_error(error_msg):
    """
    记录错误日志
    
    Args:
        error_msg (str): 错误信息
    """
    logger.error(f"[错误] {error_msg}")


def log_startup():
    """记录程序启动日志"""
    from config import APP_NAME, VERSION
    logger.info("=" * 50)
    logger.info(f"{APP_NAME} v{VERSION} 启动")
    logger.info("=" * 50)
